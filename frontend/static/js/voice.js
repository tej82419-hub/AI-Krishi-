/**
 * AI Krishi – Voice Assistant Module
 * Handles Speech Recognition and Text-to-Speech
 */

const Voice = (() => {
    let recognition = null;
    let isListening = false;
    let currentLang = 'en';

    // Language to BCP47 locale mapping for Web Speech API
    const LANG_MAP = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'ta': 'ta-IN',
        'te': 'te-IN'
    };

    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const isSupported = !!SpeechRecognition;

    function setLanguage(lang) {
        currentLang = lang;
        if (recognition) {
            recognition.lang = LANG_MAP[lang] || 'en-IN';
        }
    }

    function setupRecognition(onResult, onEnd, onError) {
        if (!isSupported) return null;

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
        recognition.lang = LANG_MAP[currentLang] || 'en-IN';

        let finalTranscript = '';
        let interimTranscript = '';

        recognition.onstart = () => {
            isListening = true;
            finalTranscript = '';
        };

        recognition.onresult = (event) => {
            interimTranscript = '';
            finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            const current = finalTranscript || interimTranscript;
            if (onResult) onResult(current, !!finalTranscript);
        };

        recognition.onend = () => {
            isListening = false;
            if (onEnd) onEnd(finalTranscript);
        };

        recognition.onerror = (event) => {
            isListening = false;
            let errorMsg = '';
            switch (event.error) {
                case 'not-allowed':
                case 'permission-denied':
                    errorMsg = 'Microphone access denied. Please allow microphone permission in browser settings.';
                    break;
                case 'no-speech':
                    errorMsg = 'No speech detected. Please try again and speak clearly.';
                    break;
                case 'network':
                    errorMsg = 'Network error. Please check your internet connection.';
                    break;
                case 'audio-capture':
                    errorMsg = 'No microphone found. Please connect a microphone.';
                    break;
                default:
                    errorMsg = `Voice recognition error: ${event.error}`;
            }
            if (onError) onError(errorMsg);
        };

        return recognition;
    }

    function start(onResult, onEnd, onError) {
        if (!isSupported) {
            if (onError) onError('Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
            return false;
        }
        if (isListening) {
            stop();
            return false;
        }
        try {
            setupRecognition(onResult, onEnd, onError);
            recognition.start();
            return true;
        } catch (e) {
            if (onError) onError('Could not start microphone: ' + e.message);
            return false;
        }
    }

    function stop() {
        if (recognition && isListening) {
            recognition.stop();
        }
        isListening = false;
    }

    function speak(text, lang = 'en', onEnd = null) {
        if (!window.speechSynthesis) return;

        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        // Clean markdown from text
        const cleanText = text
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1')
            .replace(/#{1,6}\s/g, '')
            .replace(/`(.*?)`/g, '$1')
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
            .replace(/---/g, '')
            .trim();

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = LANG_MAP[lang] || 'en-IN';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;

        // Try to use an Indian English voice
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v =>
            v.lang === utterance.lang ||
            v.lang.startsWith(lang) ||
            (lang === 'en' && v.lang.includes('IN'))
        );
        if (preferredVoice) utterance.voice = preferredVoice;

        utterance.onend = onEnd;
        utterance.onerror = (e) => {
            console.warn('TTS error:', e.error);
            if (onEnd) onEnd();
        };

        window.speechSynthesis.speak(utterance);
    }

    function stopSpeaking() {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    }

    return {
        isSupported,
        start,
        stop,
        speak,
        stopSpeaking,
        setLanguage,
        get isListening() { return isListening; }
    };
})();
