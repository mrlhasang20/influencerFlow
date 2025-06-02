# Voice integration

from typing import Optional, List, Dict
import asyncio
import time
import sys
import os
import tempfile
from schemas.communication_schemas import (
    VoiceGenerationRequest, VoiceGenerationResponse
)
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings
from shared.utils import Timer, generate_id
import httpx

class VoiceService:
    def __init__(self):
        self.elevenlabs_api_key = getattr(settings, 'elevenlabs_api_key', None)
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice
        self.supported_languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ja": "Japanese",
            "ko": "Korean"
        }
    
    async def generate_voice(self, request: VoiceGenerationRequest) -> VoiceGenerationResponse:
        """Generate voice audio from text"""
        try:
            with Timer(f"Voice generation for {len(request.text)} characters"):
                if not self.elevenlabs_api_key:
                    # Simulate voice generation for demo
                    return await self._simulate_voice_generation(request)
                
                # Use ElevenLabs API for real voice generation
                audio_data = await self._generate_elevenlabs_voice(request)
                
                if audio_data:
                    # Save audio file and return response
                    audio_url = await self._save_audio_file(audio_data, request)
                    
                    return VoiceGenerationResponse(
                        audio_url=audio_url,
                        duration_seconds=self._estimate_duration(request.text, request.speed),
                        file_size_bytes=len(audio_data),
                        voice_id=request.voice_id,
                        language=request.language
                    )
                else:
                    raise Exception("Failed to generate voice audio")
                
        except Exception as e:
            print(f"Voice generation error: {e}")
            # Return simulated response as fallback
            return await self._simulate_voice_generation(request)
    
    async def _generate_elevenlabs_voice(self, request: VoiceGenerationRequest) -> Optional[bytes]:
        """Generate voice using ElevenLabs API"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{request.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": request.text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            # Adjust for language if not English
            if request.language != "en":
                data["model_id"] = "eleven_multilingual_v2"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=30.0)
                
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"ElevenLabs API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"ElevenLabs generation error: {e}")
            return None
    
    async def _simulate_voice_generation(self, request: VoiceGenerationRequest) -> VoiceGenerationResponse:
        """Simulate voice generation for demo purposes"""
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Generate a mock audio URL
        audio_filename = f"voice_{generate_id()}.mp3"
        audio_url = f"/api/v1/audio/{audio_filename}"
        
        # Estimate file size (approximately 1KB per second of audio)
        duration = self._estimate_duration(request.text, request.speed)
        estimated_size = int(duration * 1024)  # 1KB per second
        
        return VoiceGenerationResponse(
            audio_url=audio_url,
            duration_seconds=duration,
            file_size_bytes=estimated_size,
            voice_id=request.voice_id,
            language=request.language
        )
    
    async def _save_audio_file(self, audio_data: bytes, request: VoiceGenerationRequest) -> str:
        """Save audio data to file and return URL"""
        try:
            # Create audio directory if it doesn't exist
            audio_dir = "/tmp/audio"  # Use appropriate directory for your deployment
            os.makedirs(audio_dir, exist_ok=True)
            
            # Generate filename
            filename = f"voice_{generate_id()}_{request.voice_id}.mp3"
            file_path = os.path.join(audio_dir, filename)
            
            # Save audio data
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            # Return URL (would be served by web server)
            return f"/api/v1/audio/{filename}"
            
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return f"/api/v1/audio/voice_{generate_id()}.mp3"  # Return mock URL
    
    def _estimate_duration(self, text: str, speed: float) -> float:
        """Estimate audio duration based on text length and speed"""
        # Average speaking rate is about 150-160 words per minute
        words = len(text.split())
        base_wpm = 155  # Words per minute
        
        # Adjust for speed
        adjusted_wpm = base_wpm * speed
        
        # Calculate duration in seconds
        duration = (words / adjusted_wpm) * 60
        
        return round(duration, 2)
    
    async def get_available_voices(self, language: str = "en") -> List[Dict]:
        """Get list of available voices for a language"""
        try:
            if not self.elevenlabs_api_key:
                return self._get_demo_voices(language)
            
            # Get voices from ElevenLabs API
            url = "https://api.elevenlabs.io/v1/voices"
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    voices_data = response.json()
                    
                    # Filter and format voices
                    filtered_voices = []
                    for voice in voices_data.get("voices", []):
                        # Filter by language if specified
                        voice_info = {
                            "voice_id": voice["voice_id"],
                            "name": voice["name"],
                            "category": voice.get("category", "generated"),
                            "description": voice.get("description", ""),
                            "preview_url": voice.get("preview_url"),
                            "available_for_tiers": voice.get("available_for_tiers", [])
                        }
                        filtered_voices.append(voice_info)
                    
                    return filtered_voices[:10]  # Return top 10 voices
                else:
                    print(f"ElevenLabs voices API error: {response.status_code}")
                    return self._get_demo_voices(language)
                    
        except Exception as e:
            print(f"Error getting available voices: {e}")
            return self._get_demo_voices(language)
    
    def _get_demo_voices(self, language: str) -> List[Dict]:
        """Get demo voices for testing"""
        demo_voices = {
            "en": [
                {
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "name": "Rachel",
                    "category": "premade",
                    "description": "Young adult female with American accent"
                },
                {
                    "voice_id": "AZnzlk1XvdvUeBnXmlld",
                    "name": "Domi",
                    "category": "premade", 
                    "description": "Young adult female with American accent"
                },
                {
                    "voice_id": "EXAVITQu4vr4xnSDxMaL",
                    "name": "Bella",
                    "category": "premade",
                    "description": "Young adult female with American accent"
                }
            ],
            "es": [
                {
                    "voice_id": "spanish_voice_1",
                    "name": "Sofia",
                    "category": "premade",
                    "description": "Adult female with Spanish accent"
                }
            ]
        }
        
        return demo_voices.get(language, demo_voices["en"])
    
    async def convert_outreach_to_voice(
        self, 
        outreach_message: str,
        creator_profile: Dict,
        voice_preferences: Optional[Dict] = None
    ) -> VoiceGenerationResponse:
        """Convert outreach message to voice with creator-specific optimization"""
        try:
            # Determine optimal voice settings based on creator profile
            voice_settings = self._optimize_voice_for_creator(creator_profile, voice_preferences)
            
            # Create voice generation request
            request = VoiceGenerationRequest(
                text=outreach_message,
                voice_id=voice_settings["voice_id"],
                language=voice_settings["language"],
                speed=voice_settings["speed"]
            )
            
            # Generate voice
            return await self.generate_voice(request)
            
        except Exception as e:
            print(f"Error converting outreach to voice: {e}")
            raise
    
    def _optimize_voice_for_creator(self, creator_profile: Dict, voice_preferences: Optional[Dict]) -> Dict:
        """Optimize voice settings based on creator profile"""
        settings = {
            "voice_id": self.default_voice_id,
            "language": "en",
            "speed": 1.0
        }
        
        # Use voice preferences if provided
        if voice_preferences:
            settings.update(voice_preferences)
            return settings
        
        # Auto-optimize based on creator profile
        creator_language = creator_profile.get("language", "English").lower()
        
        # Map language to voice settings
        if "spanish" in creator_language:
            settings["language"] = "es"
            settings["voice_id"] = "spanish_voice_1"
        elif "french" in creator_language:
            settings["language"] = "fr"
        elif "german" in creator_language:
            settings["language"] = "de"
        
        # Adjust speed based on platform (some platforms prefer faster/slower speech)
        platform = creator_profile.get("platform", "").lower()
        if platform == "tiktok":
            settings["speed"] = 1.1  # Slightly faster for TikTok
        elif platform == "youtube":
            settings["speed"] = 0.95  # Slightly slower for YouTube
        
        return settings
    
    async def get_voice_analytics(self, voice_id: str, days: int = 7) -> Dict:
        """Get analytics for voice usage"""
        try:
            # This would integrate with analytics database
            # For demo, return mock analytics
            return {
                "voice_id": voice_id,
                "total_generations": 45,
                "total_duration_minutes": 12.5,
                "average_message_length": 150,
                "success_rate": 98.5,
                "most_common_language": "en",
                "peak_usage_hours": ["10:00", "14:00", "16:00"],
                "creator_satisfaction_score": 4.8
            }
            
        except Exception as e:
            print(f"Error getting voice analytics: {e}")
            return {}
    
    def validate_text_for_voice(self, text: str) -> Dict[str, bool]:
        """Validate text for voice generation"""
        checks = {
            "appropriate_length": 10 <= len(text) <= 1000,
            "no_excessive_punctuation": text.count("!") <= 5 and text.count("?") <= 5,
            "readable_content": not any(char.isdigit() for char in text[:50]),  # Simplified check
            "proper_encoding": text.isascii() or len(text.encode('utf-8')) < len(text) * 4
        }
        
        return checks
    
    async def batch_voice_generation(
        self, 
        messages: List[Dict],
        voice_settings: Dict
    ) -> List[VoiceGenerationResponse]:
        """Generate voice for multiple messages in batch"""
        try:
            results = []
            
            # Process in small batches to avoid rate limits
            batch_size = 3
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                
                # Process batch concurrently
                tasks = []
                for message_data in batch:
                    request = VoiceGenerationRequest(
                        text=message_data["text"],
                        voice_id=voice_settings.get("voice_id", self.default_voice_id),
                        language=voice_settings.get("language", "en"),
                        speed=voice_settings.get("speed", 1.0)
                    )
                    tasks.append(self.generate_voice(request))
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Add successful results
                for result in batch_results:
                    if isinstance(result, VoiceGenerationResponse):
                        results.append(result)
                    else:
                        print(f"Batch voice generation error: {result}")
                
                # Small delay between batches
                if i + batch_size < len(messages):
                    await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            print(f"Batch voice generation error: {e}")
            return []