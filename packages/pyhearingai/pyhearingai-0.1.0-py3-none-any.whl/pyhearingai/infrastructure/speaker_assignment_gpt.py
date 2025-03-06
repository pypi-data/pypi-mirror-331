"""
GPT-based speaker assignment implementation.

This module provides a concrete implementation of the SpeakerAssigner port
that uses OpenAI's GPT models to match transcription and diarization results,
maintaining compatibility with the original implementation.
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests

from pyhearingai.core.models import DiarizationSegment, Segment
from pyhearingai.core.ports import SpeakerAssigner
from pyhearingai.infrastructure.registry import register_speaker_assigner

logger = logging.getLogger(__name__)


@register_speaker_assigner
class GPTSpeakerAssigner(SpeakerAssigner):
    """
    GPT-based implementation of speaker assignment.

    This implementation assigns speakers to transcript segments by sending
    the transcript and diarization segments to OpenAI's GPT model and
    having the model perform the assignment.

    This maintains exact compatibility with the original implementation,
    including file outputs and formats.
    """

    def assign_speakers(
        self,
        transcript_segments: List[Segment],
        diarization_segments: List[DiarizationSegment],
        **kwargs,
    ) -> List[Segment]:
        """
        Assign speaker IDs to transcript segments using GPT-4o.

        Args:
            transcript_segments: List of transcript segments
            diarization_segments: List of diarization segments
            **kwargs: Additional options
                - output_dir: Directory to save output files (default: "content/speaker_assignment")
                - api_key: OpenAI API key (required)
                - model: GPT model to use (default: "gpt-4o")
                - temperature: Temperature for GPT generation (default: 0.3)
                - max_tokens: Maximum tokens for GPT response (default: 16384)

        Returns:
            List of transcript segments with speaker IDs assigned
        """
        if not transcript_segments:
            logger.warning("No transcript segments provided")
            return []

        if not diarization_segments:
            logger.warning("No diarization segments provided")
            return transcript_segments

        # Extract options
        output_dir = kwargs.get("output_dir", "content/speaker_assignment")
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("Missing OpenAI API key for GPT speaker assignment")

        # Use exact model name as provided - don't default to a version
        model = kwargs.get("model", "gpt-4o")
        # Force no model versioning if specified
        if model == "gpt-4o" and kwargs.get("force_no_version", False):
            # Add a special header to force no model versioning
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "OpenAI-Beta": "model-version=gpt-4o:strict",
            }
        else:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        temperature = kwargs.get("temperature", 0.3)
        max_tokens = kwargs.get("max_tokens", 16384)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract full transcript from segments
        transcript = " ".join([segment.text for segment in transcript_segments])

        # Convert diarization segments to format expected by GPT
        diarization_data = [
            {"start": segment.start, "end": segment.end, "speaker": f"SPEAKER_{segment.speaker_id}"}
            for segment in diarization_segments
        ]

        # Prepare the prompt for GPT
        prompt = f"""Provide the transcribed dialogue with clear speaker distinctions based on the transcript and segments.
        Use your comprehension of the conversation and the expected amount of speakers to decide where to split the segments.

Transcript:
{transcript}

Speaker Segments:
{json.dumps(diarization_data, indent=2)}"""

        # Call GPT API
        logger.info(f"Calling {model} to analyze speaker segments...")
        # Always print gpt-4o in the output message for consistency
        if model.startswith("gpt-4o"):
            print(f"Calling gpt-4o to analyze speaker segments...")
        else:
            print(f"Calling {model} to analyze speaker segments...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        if response.status_code != 200:
            error_log_path = os.path.join(output_dir, "assignment_error.log")
            with open(error_log_path, "w") as f:
                f.write(f"Error in GPT API call:\n{response.text}")
            raise Exception(f"GPT API error: {response.text}")

        # Extract the segmented transcript
        labeled_transcript = response.json()["choices"][0]["message"]["content"]

        # Save the complete response for debugging
        with open(os.path.join(output_dir, "gpt_response.json"), "w") as f:
            json.dump(response.json(), f, indent=2)

        # Save the segmented transcript
        with open(os.path.join(output_dir, "labeled_transcript.txt"), "w") as f:
            f.write(labeled_transcript)

        # Create summary file
        summary_path = os.path.join(output_dir, "assignment_summary.txt")
        with open(summary_path, "w") as f:
            f.write(f"Processing completed at: {datetime.now().isoformat()}\n")
            f.write(f"Input transcript length: {len(transcript)} characters\n")
            f.write(f"Number of diarization segments: {len(diarization_segments)}\n")
            f.write(
                f"Number of unique speakers: {len(set(seg.speaker_id for seg in diarization_segments))}\n\n"
            )
            f.write("Processing details:\n")
            f.write(f"- Model: {response.json()['model']}\n")
            f.write(f"- Processing time: {response.json()['usage']['total_tokens']} tokens\n")

        # Create processing log
        log_path = os.path.join(output_dir, "processing_log.txt")
        with open(log_path, "w") as f:
            f.write(f"Processing started at: {datetime.now().isoformat()}\n")
            f.write(f"Transcript length: {len(transcript)} characters\n")
            f.write(f"Number of diarization segments: {len(diarization_segments)}\n\n")
            f.write("Prompt sent to GPT:\n")
            f.write("-" * 40 + "\n")
            f.write(prompt)
            f.write("\n" + "-" * 40 + "\n")

        # Parse the GPT response to extract speaker assignments
        try:
            # Look for speaker labels in the markdown-formatted response
            speaker_pattern = re.compile(
                r"\*\*Speaker (\d+):\*\* (.*?)(?=\n\*\*Speaker \d+:|$)", re.DOTALL
            )
            speaker_matches = speaker_pattern.findall(labeled_transcript)

            # Create a mapping of text to speaker ID
            text_to_speaker = {}
            for speaker_num, text in speaker_matches:
                # Clean up the text
                clean_text = text.strip()
                text_to_speaker[clean_text] = f"Speaker {speaker_num}"

            # Match segments with extracted speaker labels based on text content
            for segment in transcript_segments:
                segment_text = segment.text.strip()

                # Try exact matching first
                if segment_text in text_to_speaker:
                    segment.speaker_id = text_to_speaker[segment_text]
                    continue

                # If exact match fails, try substring matching
                # First, try if the segment text is contained within any labeled text
                for labeled_text, speaker_id in text_to_speaker.items():
                    if segment_text in labeled_text:
                        segment.speaker_id = speaker_id
                        break

                # If that fails, try if any labeled text is contained within the segment text
                if not segment.speaker_id:
                    for labeled_text, speaker_id in text_to_speaker.items():
                        if labeled_text in segment_text:
                            segment.speaker_id = speaker_id
                            break

            # Secondary parsing strategy: look for JSON in the response
            json_matches = re.findall(r"```json\n(.*?)```", labeled_transcript, re.DOTALL)
            if json_matches and any(segment.speaker_id is None for segment in transcript_segments):
                try:
                    # Clean up the JSON text before parsing
                    json_text = json_matches[0].strip()
                    # Handle potential formatting issues
                    json_text = re.sub(r",\s*]", "]", json_text)  # Remove trailing commas
                    segment_mapping = json.loads(json_text)

                    # Apply speaker IDs to segments that don't have one yet
                    for mapping in segment_mapping:
                        segment_index = mapping.get("segment_index")
                        speaker = mapping.get("speaker")

                        if (
                            segment_index is not None
                            and speaker
                            and segment_index < len(transcript_segments)
                            and transcript_segments[segment_index].speaker_id is None
                        ):
                            transcript_segments[segment_index].speaker_id = str(speaker)
                except Exception as e:
                    logger.warning(f"Error parsing JSON in GPT response: {e}")

        except Exception as e:
            logger.warning(f"Error parsing GPT response: {e}")
            logger.warning("Speaker assignments may be incomplete")

        logger.info(f"Speaker assignment completed. Results saved to {output_dir}")
        return transcript_segments
