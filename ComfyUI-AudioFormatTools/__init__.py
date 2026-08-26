import torch


class AudioSilenceExtend:
    """
    ComfyUI 自定义节点：
    输入 AUDIO，在音频前面或后面追加指定秒数的静音。
    适合 Load Audio 读取 flac / mp3 / wav 后直接延长音频长度。
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "extend_seconds": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 3600.0,
                        "step": 0.1,
                        "display": "number",
                    },
                ),
                "position": (
                    ["append_end", "prepend_start"],
                    {
                        "default": "append_end",
                    },
                ),
            }
        }

    RETURN_TYPES = ("AUDIO", "FLOAT", "FLOAT")
    RETURN_NAMES = ("audio", "old_seconds", "new_seconds")
    FUNCTION = "extend_audio"
    CATEGORY = "audio"

    def extend_audio(self, audio, extend_seconds, position):
        if audio is None:
            raise ValueError("AudioSilenceExtend: 输入 audio 为空。")

        if "waveform" not in audio or "sample_rate" not in audio:
            raise ValueError("AudioSilenceExtend: AUDIO 必须包含 waveform 和 sample_rate。")

        waveform = audio["waveform"]
        sample_rate = int(audio["sample_rate"])

        if not isinstance(waveform, torch.Tensor):
            raise TypeError("AudioSilenceExtend: waveform 必须是 torch.Tensor。")

        if waveform.ndim != 3:
            raise ValueError(
                f"AudioSilenceExtend: waveform 维度应为 [B, C, T]，当前是 {list(waveform.shape)}。"
            )

        extend_seconds = max(0.0, float(extend_seconds))
        silence_samples = int(round(extend_seconds * sample_rate))

        old_samples = waveform.shape[-1]
        old_seconds = old_samples / sample_rate

        if silence_samples <= 0:
            new_audio = {
                **audio,
                "waveform": waveform.clone(),
                "sample_rate": sample_rate,
            }
            return (new_audio, float(old_seconds), float(old_seconds))

        batch, channels, _ = waveform.shape

        silence = torch.zeros(
            (batch, channels, silence_samples),
            dtype=waveform.dtype,
            device=waveform.device,
        )

        if position == "prepend_start":
            new_waveform = torch.cat([silence, waveform], dim=-1)
        else:
            new_waveform = torch.cat([waveform, silence], dim=-1)

        new_seconds = new_waveform.shape[-1] / sample_rate

        new_audio = {
            **audio,
            "waveform": new_waveform,
            "sample_rate": sample_rate,
        }

        return (new_audio, float(old_seconds), float(new_seconds))


class AudioTrim:
    """
    ComfyUI 自定义节点：
    输入 AUDIO，从音频前面或后面裁掉指定秒数。
    适合在延长或处理后快速缩短音频首尾长度。
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "trim_seconds": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 3600.0,
                        "step": 0.1,
                        "display": "number",
                    },
                ),
                "position": (
                    ["trim_end", "trim_start"],
                    {
                        "default": "trim_end",
                    },
                ),
            }
        }

    RETURN_TYPES = ("AUDIO", "FLOAT", "FLOAT")
    RETURN_NAMES = ("audio", "old_seconds", "new_seconds")
    FUNCTION = "trim_audio"
    CATEGORY = "audio"

    def trim_audio(self, audio, trim_seconds, position):
        if audio is None:
            raise ValueError("AudioTrim: 输入 audio 为空。")

        if "waveform" not in audio or "sample_rate" not in audio:
            raise ValueError("AudioTrim: AUDIO 必须包含 waveform 和 sample_rate。")

        waveform = audio["waveform"]
        sample_rate = int(audio["sample_rate"])

        if not isinstance(waveform, torch.Tensor):
            raise TypeError("AudioTrim: waveform 必须是 torch.Tensor。")

        if waveform.ndim != 3:
            raise ValueError(
                f"AudioTrim: waveform 维度应为 [B, C, T]，当前是 {list(waveform.shape)}。"
            )

        trim_seconds = max(0.0, float(trim_seconds))
        trim_samples = int(round(trim_seconds * sample_rate))

        old_samples = waveform.shape[-1]
        old_seconds = old_samples / sample_rate

        if trim_samples <= 0:
            new_waveform = waveform.clone()
        else:
            trim_samples = min(trim_samples, old_samples)

            if position == "trim_start":
                new_waveform = waveform[..., trim_samples:].clone()
            else:
                keep_samples = old_samples - trim_samples
                new_waveform = waveform[..., :keep_samples].clone()

        new_seconds = new_waveform.shape[-1] / sample_rate

        new_audio = {
            **audio,
            "waveform": new_waveform,
            "sample_rate": sample_rate,
        }

        return (new_audio, float(old_seconds), float(new_seconds))


NODE_CLASS_MAPPINGS = {
    "AudioSilenceExtend": AudioSilenceExtend,
    "AudioTrim": AudioTrim,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioSilenceExtend": "Audio Silence Extend / 音频静音延长",
    "AudioTrim": "Audio Trim / 音频首尾缩短",
}
