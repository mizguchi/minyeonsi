(() => {
  "use strict";

  function fitScreen() {
    const screen = document.querySelector("#game-screen");
    if (!screen) return;
    const scale = Math.min(window.innerWidth / 1280, window.innerHeight / 720, 1);
    screen.style.transform = `scale(${scale})`;
  }

  window.runDialogue = function runDialogue(steps, nextUrl, onDone) {
    const queue = [...steps];
    const dialogue = document.querySelector("#dialogue");
    const speaker = document.querySelector("#speaker");
    const line = document.querySelector("#line");
    const profile = document.querySelector("#profile-card");
    const profileNext = document.querySelector("#profile-next");
    const character = document.querySelector("#character");
    const effect = document.querySelector("#effect");
    const sprite = document.querySelector("#sprite");
    const spriteMotionClasses = ["motion-enter", "motion-goddess"];
    let spriteHasEntered = false;

    // 다음 PNG를 미리 받아 두어 스프라이트 교체 순간에 이전 인물이 끼어 보이지 않게 한다.
    const spritePreloads = [...new Set(steps.map((step) => step.sprite).filter(Boolean))]
      .map((spriteName) => {
        const image = new Image();
        image.decoding = "async";
        image.src = `/static/img/${spriteName}.png`;
        image.decode?.().catch(() => {});
        return image;
      });

    function playSpriteMotion(className) {
      if (!sprite || !className || sprite.classList.contains("hidden")) return;
      sprite.classList.remove(...spriteMotionClasses);
      // 같은 동작이 연속으로 와도 애니메이션을 처음부터 다시 실행한다.
      void sprite.offsetWidth;
      sprite.classList.add(className);
    }

    sprite?.addEventListener("animationend", (event) => {
      if (event.animationName.startsWith("sprite")) {
        sprite.classList.remove(...spriteMotionClasses);
      }
    });

    // 호감도 숫자: 대사 시작 땐 '변화 전' 값으로 되돌려두고, 효과 스텝에서 같이 올린다
    const score = document.querySelector("#score");
    const totalEffect = steps.reduce((sum, s) => sum + (typeof s.effect === "number" ? s.effect : 0), 0);
    let shownScore = null;
    if (score && totalEffect !== 0) {
      const finalScore = parseInt(score.textContent, 10);
      if (!Number.isNaN(finalScore)) {
        shownScore = finalScore - totalEffect;
        score.textContent = shownScore;
      }
    }

    const TYPE_SPEED = 32; // 글자당 ms
    let typing = false;
    let typeTimer = null;
    let currentText = "";

    function typeLine(text) {
      window.clearTimeout(typeTimer);
      currentText = text;
      typing = true;
      line.textContent = "";
      let i = 0;
      (function step() {
        if (i <= text.length) {
          line.textContent = text.slice(0, i);
          i += 1;
          typeTimer = window.setTimeout(step, TYPE_SPEED);
        } else {
          typing = false;
        }
      })();
    }

    function revealAll() {
      window.clearTimeout(typeTimer);
      line.textContent = currentText;
      typing = false;
    }

    function handleTap() {
      if (typing) {
        revealAll();
      } else {
        advance();
      }
    }

    function finish() {
      window.clearTimeout(typeTimer);
      spritePreloads.length = 0;
      dialogue?.removeEventListener("click", handleTap);
      dialogue?.removeEventListener("keydown", onKey);
      dialogue?.classList.add("hidden");
      if (onDone) {
        onDone();
      } else if (nextUrl) {
        window.location.href = nextUrl;
      }
    }

    function advance() {
      profile?.classList.add("hidden");
      const step = queue.shift();
      if (!step) return finish();

      if (step.profile) {
        dialogue?.classList.add("hidden");
        profile?.classList.remove("hidden");
        sprite?.classList.add("hidden"); // 소개 화면은 캐릭터 없이 배경만
        return;
      }

      const hasSpeaker = Boolean(step.speaker);
      speaker.textContent = step.speaker || "";
      speaker.classList.toggle("hidden", !hasSpeaker);
      dialogue.classList.toggle("narration", !hasSpeaker);
      dialogue.classList.remove("hidden");
      typeLine(step.text);

      if (character && step.mood) character.dataset.mood = step.mood;
      // 캐릭터 스프라이트: step.sprite = "boy/opening4" 처럼 폴더/파일명 지정 (미지정이면 그대로 유지, ""이면 숨김)
      if (sprite && step.sprite !== undefined) {
        if (step.sprite) {
          sprite.dataset.spriteKey = step.sprite;
          sprite.src = `/static/img/${step.sprite}.png`;
          sprite.classList.remove("hidden");
        } else {
          delete sprite.dataset.spriteKey;
          sprite.classList.remove(...spriteMotionClasses);
          sprite.classList.add("hidden");
        }
      }
      // 위치 지정: step.pos = "left" | "right" | "center"(기본)
      if (sprite && step.pos !== undefined) {
        sprite.classList.remove("pos-left", "pos-right");
        if (step.pos === "left") sprite.classList.add("pos-left");
        else if (step.pos === "right") sprite.classList.add("pos-right");
      }

      if (sprite && !sprite.classList.contains("hidden")) {
        if (step.motion) {
          spriteHasEntered = true;
          playSpriteMotion(`motion-${step.motion}`);
        } else if (!spriteHasEntered) {
          spriteHasEntered = true;
          playSpriteMotion("motion-enter");
        }
      }

      if (effect && typeof step.effect === "number") {
        effect.textContent = `호감도 ${step.effect > 0 ? "+" : ""}${step.effect}`;
        effect.className = `effect show ${step.effect > 0 ? "plus" : "minus"}`;
        window.setTimeout(() => { effect.className = "effect"; }, 1800);
        if (score && shownScore !== null) {
          shownScore += step.effect;
          score.textContent = shownScore;
        }
      }
    }

    function onKey(event) {
      if (event.key === "Enter" || event.key === " ") handleTap();
    }
    dialogue?.addEventListener("click", handleTap);
    dialogue?.addEventListener("keydown", onKey);
    profileNext?.addEventListener("click", advance);
    advance();
  };

  window.addEventListener("resize", fitScreen);
  fitScreen();
})();
