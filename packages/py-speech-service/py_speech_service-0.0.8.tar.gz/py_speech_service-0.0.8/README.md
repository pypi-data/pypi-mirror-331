# PySpeechService Developer Documentation

This documentation will cover utilizing the PySpeechService application for text-to-speech and speech recognition purposes in another application.

## Step 1: Generate gRPC Files

Use the [PySpeechService gRPC proto file](https://raw.githubusercontent.com/MattEqualsCoder/PySpeechService/refs/heads/main/python/speech_service.proto) to generate the files needed to utilize the service.

## Step 2: Launch the PySpeechService Application

Launch the PySpeechService application, keeping in mind that the application can be setup in multiple ways.

* Executable in path - Simply execute PySpeechService
* Python module - `python -m py-speech-service` or `python3 -m py-speech-service` or `py -m py-speech-service`
* Local app folder - `~/.local/share/py_speech_service/py-speech-service` or `%localappdata%/py_speech_service/py-speech-service.exe`

Once it's launched, read the application output. The first line is a JSON message to give information about PySpeechService as it waits for the a connection.

```
{
    "version": "0.1.0",
    "port": 12345
}
```

The version is the current version of the PySpeechService, which can be used to verify compatibility. The port is the random port used by the PySpeechService application for gRPC.

## Step 3: Connect to the PySpeechService gRPC Channel

Using gRPC generated code and the standards for gRPC usage for the language of your application, connect to the PySpeechService channel and client, then call StartSpeechService. StartSpeechService is a two-way stream of SpeechServiceRequests and SpeechServiceResponses.

Use the stream to send SpeechServiceRequests to PySpeechService to initialize and use TTS and speech recognition. You'll then listen to the stream's SpeechServiceResponses to receive updates on when initialization is complete, when TTS starts and stops, and when speech has been recognized.

## Step 4: Initialize TTS

Before you use TTS, you need to first send a request to PySpeechService informing it of the defaults to use for TTS. This allows it to do a few things. First, it'll tell PySpeechService to download any files necessary. Second, it gives it default information to use when sending text to use for TTS.

The following is an example of the request you can send:

```
{
    "set_speech_settings": {
        "speech_settings": {
            "model_name": "hfc_female"
        },
    }
}
```

The model name is the name of a [Piper TTS model](https://github.com/rhasspy/piper/blob/master/VOICES.md). If you have an onnx and config file for a Piper voice, you can also pass that in for the 