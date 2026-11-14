# 두근두근 민정이의 마음을 얻어라

Flask 서버와 여러 페이지로 구성한 웹 미연시 CTF 문제입니다. 화면은 Ren'Py의 기본적인 대화창과 선택지 구성을 따릅니다.

## 설치와 실행

```powershell
python -m pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:5000`으로 접속합니다.

## Docker 실행

운영 환경에서는 Flask 개발 서버 대신 Gunicorn을 사용합니다. `flag.txt`는 Docker 이미지에 포함되지 않으며 플래그와 세션 키는 환경 변수로 전달합니다.

```powershell
docker build -t minyeonsi:latest .
docker run --rm -p 8080:8080 `
  -e FLASK_SECRET_KEY="충분히-긴-임의의-비밀키" `
  -e CHALLENGE_FLAG="WHOIS{배포용_플래그}" `
  minyeonsi:latest
```

브라우저에서 `http://127.0.0.1:8080`으로 접속합니다. AWS에 배포할 때도 `FLASK_SECRET_KEY`와 `CHALLENGE_FLAG`를 이미지에 넣지 말고 ECS 작업 정의나 App Runner 환경 변수/Secrets Manager로 주입해야 합니다.

## 페이지 구성

- `/` 이름 입력
- `/opening` 오프닝과 민정 소개
- `/game` 무작위 선택지 3개
- `/joke` 아재개그와 CSTI 입력
- `/activity/...` 일반 행동 결과
- `/meal` 식당 선택
- `/confession` 고백
- `/ending` 서버 판정을 통과한 경우에만 플래그 표시

## 플래그 관리

플래그는 HTML과 JavaScript에 들어 있지 않습니다. 서버는 다음 순서로 플래그를 읽습니다.

1. `CHALLENGE_FLAG` 환경 변수
2. 프로젝트 루트의 `flag.txt`

`flag.txt`는 `.gitignore`에 포함되어 있습니다. 실제 배포 시에는 파일보다 환경 변수를 권장합니다.

## CSTI

아재개그 페이지의 입력값은 의도적으로 취약한 클라이언트 템플릿 처리기를 거칩니다. 처리된 호감도는 일회용 요청값과 함께 서버 세션에 반영됩니다.

아재개그 결과는 50% 확률로 `+1` 또는 `-1`이므로, 입력값이 10,000이어도 실패하면 최종 호감도는 9,999가 됩니다.

## 이미지 추가

현재는 PNG가 없는 상태입니다. 이미지가 준비되면 `static/styles.css`의 `.scene-*` 선택자에 배경 이미지를 연결하고, `.character-placeholder`를 캐릭터 이미지로 교체하면 됩니다.
