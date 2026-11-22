"use strict";

const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const bestScoreEl = document.getElementById("best-score");
const levelEl = document.getElementById("level");
const levelProgressEl = document.getElementById("level-progress");
const startOverlay = document.getElementById("start-overlay");
const pauseOverlay = document.getElementById("pause-overlay");
const gameoverOverlay = document.getElementById("gameover-overlay");
const finalScoreEl = document.getElementById("final-score");
const gameoverTitleEl = document.getElementById("gameover-title");
const pauseIcon = document.getElementById("pause-icon");
const soundIcon = document.getElementById("sound-icon");

const WORLD_WIDTH = 1800;
const GROUND_Y = 520;
const bestKey = "leaf-runner-best";

let player;
let platforms;
let coins;
let enemies;
let particles = [];
let clouds = [];
let keys = {};
let cameraX = 0;
let score = 0;
let level = 1;
let coinsCollected = 0;
let running = false;
let paused = false;
let won = false;
let muted = false;
let audioContext;
let animationFrame;
let lastTime = 0;
let bestScore = Number(localStorage.getItem(bestKey) || 0);

bestScoreEl.textContent = formatScore(bestScore);

function formatScore(value) {
  return String(value).padStart(4, "0");
}

function resetGame() {
  score = 0;
  level = 1;
  coinsCollected = 0;
  cameraX = 0;
  particles = [];
  setupLevel();
  running = false;
  paused = false;
  won = false;
  updateHud();
  draw();
}

function setupLevel() {
  player = { x: 90, y: 400, width: 34, height: 48, vx: 0, vy: 0, grounded: false, facing: 1 };

  platforms = [
    { x: 0, y: GROUND_Y, width: 520, height: 80 },
    { x: 590, y: GROUND_Y, width: 260, height: 80 },
    { x: 920, y: GROUND_Y, width: 360, height: 80 },
    { x: 1360, y: GROUND_Y, width: 440, height: 80 },
    { x: 280, y: 430, width: 150, height: 18 },
    { x: 650, y: 410, width: 140, height: 18 },
    { x: 1020, y: 430, width: 150, height: 18 },
    { x: 1220, y: 350, width: 130, height: 18 },
  ];

  coins = [
    { x: 330, y: 390, collected: false },
    { x: 390, y: 390, collected: false },
    { x: 700, y: 370, collected: false },
    { x: 760, y: 370, collected: false },
    { x: 1060, y: 390, collected: false },
    { x: 1270, y: 310, collected: false },
    { x: 1510, y: 470, collected: false },
  ];

  enemies = [
    { x: 480, y: 486, width: 34, height: 34, vx: 0.7, left: 420, right: 540, squashed: false },
    { x: 980, y: 486, width: 34, height: 34, vx: -0.8, left: 930, right: 1060, squashed: false },
    { x: 1450, y: 486, width: 34, height: 34, vx: 0.8, left: 1380, right: 1550, squashed: false },
  ];

  clouds = [
    { x: 160, y: 100, s: 1 },
    { x: 520, y: 155, s: 0.75 },
    { x: 950, y: 90, s: 1.15 },
    { x: 1450, y: 140, s: 0.85 },
  ];
}

function startGame() {
  ensureAudio();
  resetGame();
  running = true;
  paused = false;
  won = false;
  startOverlay.classList.add("hidden");
  pauseOverlay.classList.add("hidden");
  gameoverOverlay.classList.add("hidden");
  lastTime = performance.now();
  cancelAnimationFrame(animationFrame);
  animationFrame = requestAnimationFrame(loop);
  playTone(330, 0.1, "square");
}

function loop(time) {
  if (!running) return;
  const delta = Math.min((time - lastTime) / 16.667, 2);
  lastTime = time;
  if (!paused) update(delta);
  draw();
  animationFrame = requestAnimationFrame(loop);
}

function update(delta) {
  const acceleration = keys.ArrowLeft || keys.KeyA ? -0.55
    : keys.ArrowRight || keys.KeyD ? 0.55 : 0;

  player.vx += acceleration * delta;
  player.vx *= 0.82;
  player.vx = Math.max(-5.2, Math.min(5.2, player.vx));

  if (acceleration !== 0) player.facing = Math.sign(acceleration);

  if ((keys.ArrowUp || keys.KeyW || keys.Space) && player.grounded) {
    player.vy = -12;
    player.grounded = false;
    playTone(420, 0.08, "square", 0.045);
  }

  player.vy += 0.58 * delta;
  player.vy = Math.min(player.vy, 14);
  player.x += player.vx * delta;
  player.y += player.vy * delta;

  player.x = Math.max(0, Math.min(WORLD_WIDTH - player.width, player.x));
  player.grounded = false;

  platforms.forEach(platform => {
    if (rectsOverlap(player, platform)) {
      const previousBottom = player.y - player.vy * delta;
      if (previousBottom <= platform.y && player.vy >= 0) {
        player.y = platform.y - player.height;
        player.vy = 0;
        player.grounded = true;
      }
    }
  });

  if (player.y > canvas.height + 100) loseLife();

  coins.forEach(coin => {
    if (!coin.collected && circleRectOverlap(coin.x, coin.y, 12, player)) {
      coin.collected = true;
      coinsCollected += 1;
      score += 100;
      burst(coin.x, coin.y, "#ffc857", 12);
      playCoin();
      updateHud();
    }
  });

  enemies.forEach(enemy => {
    if (enemy.squashed) return;
    enemy.x += enemy.vx * delta;
    if (enemy.x < enemy.left || enemy.x > enemy.right) enemy.vx *= -1;

    if (rectsOverlap(player, enemy)) {
      const stomp = player.vy > 1 && player.y + player.height - enemy.y < 20;
      if (stomp) {
        enemy.squashed = true;
        player.vy = -8;
        score += 250;
        burst(enemy.x + 17, enemy.y + 15, "#8dd14f", 14);
        playTone(180, 0.09, "square", 0.05);
      } else {
        loseLife();
      }
    }
  });

  const finishX = 1690;
  if (player.x > finishX) finishLevel();

  particles.forEach(particle => {
    particle.x += particle.vx * delta;
    particle.y += particle.vy * delta;
    particle.vy += 0.12 * delta;
    particle.life -= delta;
  });
  particles = particles.filter(particle => particle.life > 0);

  const targetCamera = Math.max(0, Math.min(WORLD_WIDTH - canvas.width, player.x - canvas.width * 0.38));
  cameraX += (targetCamera - cameraX) * 0.08 * delta;
}

function rectsOverlap(a, b) {
  return a.x < b.x + b.width &&
    a.x + a.width > b.x &&
    a.y < b.y + b.height &&
    a.y + a.height > b.y;
}

function circleRectOverlap(cx, cy, radius, rect) {
  const nearestX = Math.max(rect.x, Math.min(cx, rect.x + rect.width));
  const nearestY = Math.max(rect.y, Math.min(cy, rect.y + rect.height));
  return (cx - nearestX) ** 2 + (cy - nearestY) ** 2 < radius ** 2;
}

function finishLevel() {
  running = false;
  won = true;
  score += 500;
  updateBest();
  gameoverTitleEl.textContent = "Valley cleared!";
  finalScoreEl.textContent = `Score ${formatScore(score)}  •  Coins ${coinsCollected}/${coins.length}`;
  gameoverOverlay.querySelector(".eyebrow").textContent = "Level complete";
  gameoverOverlay.classList.remove("hidden");
  playWin();
}

function loseLife() {
  running = false;
  won = false;
  updateBest();
  gameoverTitleEl.textContent = "The run ends here";
  finalScoreEl.textContent = `Score ${formatScore(score)}  •  Coins ${coinsCollected}/${coins.length}`;
  gameoverOverlay.querySelector(".eyebrow").textContent = "Try again";
  gameoverOverlay.classList.remove("hidden");
  playCrash();
  draw();
}

function updateBest() {
  if (score > bestScore) {
    bestScore = score;
    localStorage.setItem(bestKey, String(bestScore));
  }
  updateHud();
}

function updateHud() {
  scoreEl.textContent = formatScore(score);
  bestScoreEl.textContent = formatScore(bestScore);
  levelEl.textContent = String(level);
  levelProgressEl.style.width = `${(coinsCollected / 7) * 100}%`;
}

function togglePause() {
  if (!running) return;
  paused = !paused;
  pauseOverlay.classList.toggle("hidden", !paused);
  pauseIcon.textContent = paused ? "▶" : "Ⅱ";
}

function draw() {
  const sky = ctx.createLinearGradient(0, 0, 0, canvas.height);
  sky.addColorStop(0, "#74c5d7");
  sky.addColorStop(1, "#d9efb4");
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  drawClouds();
  ctx.save();
  ctx.translate(-cameraX, 0);
  drawBackground();
  platforms.forEach(drawPlatform);
  coins.forEach(drawCoin);
  enemies.forEach(drawEnemy);
  drawFlag();
  drawPlayer();
  drawParticles();
  ctx.restore();
}

function drawClouds() {
  clouds.forEach(cloud => {
    const x = cloud.x - cameraX * 0.18;
    ctx.fillStyle = "rgba(255,255,255,0.72)";
    ctx.beginPath();
    ctx.arc(x, cloud.y, 24 * cloud.s, 0, Math.PI * 2);
    ctx.arc(x + 28 * cloud.s, cloud.y - 10 * cloud.s, 32 * cloud.s, 0, Math.PI * 2);
    ctx.arc(x + 62 * cloud.s, cloud.y, 24 * cloud.s, 0, Math.PI * 2);
    ctx.fill();
  });
}

function drawBackground() {
  ctx.fillStyle = "rgba(77, 130, 78, 0.28)";
  for (let x = -100; x < WORLD_WIDTH + 200; x += 180) {
    ctx.beginPath();
    ctx.moveTo(x, GROUND_Y);
    ctx.lineTo(x + 90, 260);
    ctx.lineTo(x + 180, GROUND_Y);
    ctx.fill();
  }
}

function drawPlatform(platform) {
  ctx.fillStyle = "#9a6641";
  ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
  ctx.fillStyle = "#70a84b";
  ctx.fillRect(platform.x, platform.y, platform.width, 12);
  ctx.fillStyle = "#baf05b";
  ctx.fillRect(platform.x, platform.y, platform.width, 4);
  ctx.fillStyle = "rgba(63, 39, 28, 0.18)";
  for (let x = platform.x + 12; x < platform.x + platform.width; x += 36) {
    ctx.fillRect(x, platform.y + 28, 14, 5);
  }
}

function drawCoin(coin) {
  if (coin.collected) return;
  const shimmer = 0.75 + Math.abs(Math.sin(performance.now() / 180)) * 0.25;
  ctx.save();
  ctx.translate(coin.x, coin.y);
  ctx.scale(shimmer, 1);
  ctx.fillStyle = "#ffc857";
  ctx.beginPath();
  ctx.arc(0, 0, 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#fff1a6";
  ctx.beginPath();
  ctx.arc(-3, -3, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawPlayer() {
  ctx.save();
  ctx.translate(player.x + player.width / 2, player.y);
  ctx.scale(player.facing, 1);
  ctx.fillStyle = "#f3b36b";
  ctx.fillRect(-11, 0, 22, 12);
  ctx.fillStyle = "#d94b45";
  ctx.fillRect(-17, 10, 34, 20);
  ctx.fillStyle = "#baf05b";
  ctx.fillRect(-13, 30, 26, 12);
  ctx.fillStyle = "#3d4d35";
  ctx.fillRect(-14, 42, 9, 6);
  ctx.fillRect(5, 42, 9, 6);
  ctx.fillStyle = "#2b3528";
  ctx.beginPath();
  ctx.arc(-5, 6, 2.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawEnemy(enemy) {
  if (enemy.squashed) return;
  ctx.fillStyle = "#7b4ca7";
  ctx.beginPath();
  ctx.ellipse(enemy.x + 17, enemy.y + 19, 17, 15, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#f2d6ff";
  ctx.beginPath();
  ctx.arc(enemy.x + 11, enemy.y + 15, 2.5, 0, Math.PI * 2);
  ctx.arc(enemy.x + 23, enemy.y + 15, 2.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#57316f";
  ctx.fillRect(enemy.x + 5, enemy.y + 30, 9, 5);
  ctx.fillRect(enemy.x + 20, enemy.y + 30, 9, 5);
}

function drawFlag() {
  ctx.fillStyle = "#4b4f45";
  ctx.fillRect(1694, 380, 8, 140);
  ctx.fillStyle = "#baf05b";
  ctx.beginPath();
  ctx.moveTo(1702, 390);
  ctx.lineTo(1780, 410);
  ctx.lineTo(1702, 438);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = "#2a3326";
  ctx.beginPath();
  ctx.arc(1698, 374, 10, 0, Math.PI * 2);
  ctx.fill();
}

function burst(x, y, color, count) {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 1.5 + Math.random() * 3.5;
    particles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 2,
      life: 25 + Math.random() * 15,
      color,
      size: 2 + Math.random() * 3,
    });
  }
}

function drawParticles() {
  particles.forEach(particle => {
    ctx.globalAlpha = Math.min(1, particle.life / 20);
    ctx.fillStyle = particle.color;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}

function ensureAudio() {
  if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
  if (audioContext.state === "suspended") audioContext.resume();
}

function playTone(frequency, duration, type = "square", volume = 0.06) {
  if (muted || !audioContext) return;
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
  gain.gain.setValueAtTime(volume, audioContext.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + duration);
}

function playCoin() {
  ensureAudio();
  playTone(660, 0.08, "square", 0.05);
  setTimeout(() => playTone(880, 0.08, "square", 0.04), 55);
}

function playWin() {
  [440, 554, 659, 880].forEach((frequency, index) =>
    setTimeout(() => playTone(frequency, 0.15, "triangle", 0.055), index * 90));
}

function playCrash() {
  ensureAudio();
  playTone(130, 0.28, "sawtooth", 0.07);
}

window.addEventListener("keydown", event => {
  keys[event.code] = true;
  if (["ArrowLeft", "ArrowRight", "ArrowUp", "Space"].includes(event.code)) event.preventDefault();
  if (event.code === "Escape" || event.code === "KeyP") togglePause();
});

window.addEventListener("keyup", event => {
  keys[event.code] = false;
});

document.querySelectorAll("[data-direction]").forEach(button => {
  const codes = { left: "ArrowLeft", right: "ArrowRight", up: "ArrowUp", down: "ArrowDown" };
  button.addEventListener("pointerdown", event => {
    event.preventDefault();
    keys[codes[button.dataset.direction]] = true;
  });
  button.addEventListener("pointerup", () => { keys[codes[button.dataset.direction]] = false; });
  button.addEventListener("pointerleave", () => { keys[codes[button.dataset.direction]] = false; });
});

document.getElementById("start-button").addEventListener("click", startGame);
document.getElementById("restart-button").addEventListener("click", startGame);
document.getElementById("resume-button").addEventListener("click", togglePause);
document.getElementById("pause-button").addEventListener("click", togglePause);
document.getElementById("sound-button").addEventListener("click", () => {
  muted = !muted;
  soundIcon.textContent = muted ? "×" : "♪";
});

resetGame();
