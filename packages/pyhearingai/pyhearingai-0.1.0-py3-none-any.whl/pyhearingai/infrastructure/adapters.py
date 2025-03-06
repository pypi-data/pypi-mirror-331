"""
Adapter initialization module.

This module imports all adapter implementations to ensure they are registered
with the registry when the package is imported.
"""

# Import audio converter
from pyhearingai.infrastructure.audio_converter import FFmpegAudioConverter

# Import all diarizers
from pyhearingai.infrastructure.diarizers.pyannote import PyannoteDiarizer

# Import all formatters
from pyhearingai.infrastructure.formatters import (
    JSONFormatter,
    MarkdownFormatter,
    SRTFormatter,
    TextFormatter,
    VTTFormatter,
)

# Import speaker assigners
from pyhearingai.infrastructure.speaker_assignment import DefaultSpeakerAssigner
from pyhearingai.infrastructure.speaker_assignment_gpt import GPTSpeakerAssigner

# Import all transcribers
from pyhearingai.infrastructure.transcribers.whisper_openai import WhisperOpenAITranscriber
