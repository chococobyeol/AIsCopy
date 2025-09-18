# AIsCopy

실시간 화면 번역 도구 - 사용자가 지정한 화면 영역을 실시간으로 캡처하여 AI 기반 번역을 수행합니다.

## 🚀 주요 기능

- **실시간 화면 번역**: 지정한 영역의 텍스트를 실시간으로 번역
- **오버레이 창**: 탐색기 창 스타일의 직관적인 UI
- **클릭-스루 모드**: 배경 작업에 방해되지 않는 투명 모드
- **API 호출 최적화**: 변화 감지로 불필요한 API 호출 방지
- **사용자 친화적 설정**: 직관적인 설정 UI와 단축키 커스터마이징

## 📋 요구사항

- Python 3.12+
- Google Gemini API 키
- Windows 10/11, macOS 12.0+, 또는 Ubuntu 20.04+

## 🛠️ 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/chococobyeol/AIsCopy.git
cd AIsCopy
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 앱 실행
```bash
python main.py
```

## ⚙️ 설정

첫 실행 시 설정 화면에서 다음을 설정하세요:

- **Google Gemini API 키**: [Google AI Studio](https://aistudio.google.com/)에서 발급
- **목표 언어**: 번역할 언어 선택
- **번역 모델**: gemini-2.5-flash 또는 gemini-2.5-flash-lite
- **단축키**: 클릭-스루 모드, 번역 실행 등

## 🎮 사용법

1. **번역 대상 창**: 번역하고 싶은 화면 영역에 배치
2. **번역 출력 창**: 번역 결과가 표시될 위치에 배치
3. **단축키 사용**:
   - `Ctrl+T`: 클릭-스루 모드 토글
   - `Ctrl+Shift+T`: 수동 번역 실행
   - `Ctrl+,`: 설정 열기

## 🔧 기술 스택

- **언어**: Python 3.12+
- **GUI**: PySide6 (Qt6)
- **화면 캡처**: mss
- **이미지 처리**: OpenCV, Pillow
- **AI API**: Google Gemini API
- **단축키**: pynput

## 📁 프로젝트 구조

```
AIsCopy/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 의존성 패키지
├── README.md              # 프로젝트 설명
├── AIsCopy_PRD.md         # 상세 요구사항 문서
├── core/                  # 핵심 모듈
│   ├── __init__.py
│   ├── screen_capture.py
│   ├── image_processor.py
│   └── translation_engine.py
├── ui/                    # UI 모듈
│   ├── __init__.py
│   ├── overlay_windows.py
│   ├── settings_dialog.py
│   └── main_window.py
└── utils/                 # 유틸리티
    ├── __init__.py
    ├── config_manager.py
    └── hotkey_manager.py
```

## 🚀 시작하기

1. **첫 실행**: 앱을 실행하면 초기 설정 화면이 나타납니다
2. **API 키 설정**: Google Gemini API 키를 입력하고 테스트합니다
3. **번역 설정**: 목표 언어와 모델을 선택합니다
4. **시작**: "시작하기" 버튼을 클릭하여 번역을 시작합니다

## 🎯 주요 특징

### 오버레이 창
- **번역 대상 창**: 완전 투명, 테두리만 표시
- **번역 출력 창**: 반투명 배경, 번역 결과 표시
- **드래그 앤 드롭**: 마우스로 위치와 크기 조절 가능

### 스마트 번역
- **변화 감지**: 화면 내용이 변경될 때만 번역 실행
- **API 최적화**: 불필요한 API 호출로 비용 절약
- **실시간 처리**: 빠른 번역 결과 제공

### 사용자 경험
- **직관적 UI**: 탐색기 창과 유사한 친숙한 인터페이스
- **단축키 지원**: 빠른 모드 전환 및 번역 실행
- **설정 저장**: 사용자 설정 자동 저장 및 복원

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 [Issues](https://github.com/chococobyeol/AIsCopy/issues)를 통해 연락해 주세요.

---

**AIsCopy** - AI로 더 쉽고 빠른 번역을 경험하세요! 🚀
