# ComfyUI Audio Format Tools

Adds an `Audio Re-encode MP3` node.

## Usage

Connect:

```text
Load Audio -> Audio Re-encode MP3 -> Preview/Audio Concatenate/other AUDIO nodes
```

The node encodes the input `AUDIO` to a temporary MP3 file, reads it back, and returns ComfyUI `AUDIO`.

Options:

- `bitrate`: MP3 bitrate label for UI reference.
- `sample_rate`: `0` keeps the original sample rate, or choose `44100` / `48000`.
- `channels`: keep original, force mono, or force stereo.

