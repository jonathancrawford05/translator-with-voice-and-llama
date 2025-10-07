# Bidirectional Translation Feature

## 🎯 **Overview**

Added support for bidirectional English ↔ Russian translation with automatic language detection and proper speech synthesis.

---

## ✨ **New Features**

### **Translation Directions**
- 🇺🇸 **English → Russian** (default)
- 🇷🇺 **Russian → English**

### **Smart Language Handling**
- Whisper transcribes in **both languages** (multilingual model)
- gTTS speaks output in the **correct language** automatically
- Dynamic UI placeholder changes based on direction

---

## 🔧 **What Changed**

### **1. worker.py**
- ✅ Switched to **multilingual Whisper** (`whisper-tiny` instead of `whisper-tiny.en`)
- ✅ Added **prompt templates** for both directions
- ✅ Dynamic **gTTS language** based on output (Russian or English)
- ✅ Functions now accept `direction` parameter

### **2. server.py**
- ✅ Passes `direction` parameter from frontend to worker functions

### **3. templates/index.html**
- ✅ Added **Translation Direction** dropdown with flag emojis
- ✅ Updated title to "Voice Translator"
- ✅ Updated description for bidirectional capability

### **4. static/script.js**
- ✅ Added `translationDirection` tracking variable
- ✅ Passes direction in API calls
- ✅ Updates input placeholder dynamically:
  - EN→RU: "Type in English..."
  - RU→EN: "Введите на русском языке..." (Type in Russian...)

### **5. Dockerfile**
- ✅ Downloads multilingual Whisper model during build

---

## 🎮 **How to Use**

### **English → Russian Translation**
1. Select "🇺🇸 English → 🇷🇺 Russian" from dropdown (default)
2. Type or speak in **English**
3. Get **Russian** translation (text + audio)

### **Russian → English Translation**
1. Select "🇷🇺 Russian → 🇺🇸 English" from dropdown
2. Type or speak in **Russian** (note: voice accent selector only affects English output)
3. Get **English** translation (text + audio)

### **Voice Accent**
- Only applies when **output is English** (RU→EN direction)
- Choose from US, UK, Australian, Canadian, or Indian accent
- Ignored when output is Russian

---

## 🧪 **Testing**

### **Test EN→RU:**
```
Input:  "I love you"
Output: "Я тебя люблю" (spoken in Russian)
```

### **Test RU→EN:**
```
Input:  "Привет, как дела?"
Output: "Hello, how are you?" (spoken in English)
```

---

## 📊 **Technical Details**

### **Prompt Templates**
```python
PROMPTS = {
    "en-ru": "Translate English to Russian. Reply ONLY with translation...",
    "ru-en": "Translate Russian to English. Reply ONLY with translation..."
}
```

### **Language Mapping**
```python
LANG_MAP = {
    "en-ru": "ru",  # Output language is Russian
    "ru-en": "en"   # Output language is English
}
```

### **API Flow**
```
Frontend: { userMessage, voice, direction }
    ↓
Server: Passes all params to worker
    ↓
Worker: 
  - Uses prompt template based on direction
  - Translates with Ollama
  - Speaks in correct language with gTTS
    ↓
Frontend: Displays & plays translated response
```

---

## ⚠️ **Important Notes**

1. **First run will be slower** - Whisper multilingual model needs to download (~75MB)
2. **Russian typing** - Make sure your keyboard supports Cyrillic input
3. **Voice accent** - Only affects English output (not Russian)
4. **Ollama model** - llama3.2 handles both directions well

---

## 🚀 **Deployment**

### **Local Testing**
```bash
# Install dependencies (if not already)
pip install -r requirements.txt

# Start server
python server.py

# Access at http://localhost:8000
```

### **Docker**
```bash
# Build (downloads multilingual Whisper model)
docker build -t translator-app .

# Run
docker run -p 8000:8000 translator-app
```

---

## 🎨 **UI Features**

- **Translation Direction selector** with emoji flags for visual clarity
- **Dynamic placeholder** changes language hint based on direction
- **Voice Accent selector** for English output customization
- **Light/Dark mode** toggle (existing feature)

---

## 🔮 **Future Enhancements**

Potential improvements:
- [ ] Auto-detect input language (remove need for direction selector)
- [ ] Support more language pairs (Spanish, French, German, etc.)
- [ ] Add language-specific voice variants (Russian male/female voices)
- [ ] Display confidence scores for translations
- [ ] Add translation history/memory

---

**Feature complete and ready for use! 🎉**
