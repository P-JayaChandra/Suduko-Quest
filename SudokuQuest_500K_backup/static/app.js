/**
 * Sudoku Quest - Production Client Application
 * Complete full-stack integration with authentication, authoritative server game sessions,
 * real-time Socket.IO ranked multiplayer, database achievements, statistics, and leaderboards.
 */

// ============================================================================
// GLOBAL STATE & INITIALIZATION
// ============================================================================

const AUTH_TOKEN_KEY = "sq_auth_token_v1";

let currentUser = null; // Populated from /api/auth/me
let socket = null;      // Socket.IO instance
let activeGame = null;  // Active game session metadata from /api/games

let gameState = {
  gameId: null,
  initialBoard: Array(81).fill("."),
  currentBoard: Array(81).fill("."),
  notes: Array(81).fill(null).map(() => new Set()),
  selectedCell: null,
  mistakes: 0,
  maxMistakes: 3,
  hintsUsed: 0,
  hintsRemaining: 3,
  timerSeconds: 0,
  timerInterval: null,
  isNotesMode: false,
  isPaused: false,
  isCompleted: false,
  levelNum: 4,
  difficulty: "medium",
  isDaily: false,
  isRanked: false,
  rankedMatchId: null,
  history: []
};

let masterAchievements = [];
let userUnlockedAchievements = new Set();
let activeCategoryFilter = "all";
let mmTimerInterval = null;
let mmTimerSeconds = 0;

// ============================================================================
// API CLIENT & AUTHENTICATION
// ============================================================================

async function apiRequest(url, options = {}) {
  const headers = options.headers || {};
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }
  options.headers = headers;

  try {
    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${url}:`, err);
    throw err;
  }
}

async function fetchCurrentUser() {
  try {
    const data = await apiRequest("/api/auth/me");
    if (data.authenticated && data.user) {
      currentUser = data.user;
      updateUserNavUI();
      initSocketConnection();
    } else {
      currentUser = null;
      updateUserNavUI();
    }
  } catch (e) {
    currentUser = null;
    updateUserNavUI();
  }
}

function updateUserNavUI() {
  const guestActions = document.getElementById("nav-guest-actions");
  const userActions = document.getElementById("nav-user-actions");
  
  if (currentUser) {
    if (guestActions) guestActions.style.display = "none";
    if (userActions) userActions.style.display = "flex";

    // Update nav user info
    const navName = document.getElementById("nav-username");
    const navLvl = document.getElementById("nav-user-lvl");
    const navAvatar = document.getElementById("nav-avatar-emoji");
    const navRankScore = document.getElementById("nav-rank-score");
    const navRankTier = document.getElementById("nav-rank-tier");
    const navStreakCount = document.getElementById("nav-streak-count");
    const heroStreak = document.getElementById("hero-streak-display");

    if (navName) navName.textContent = currentUser.display_name || currentUser.username;
    if (navLvl) navLvl.textContent = `Level ${currentUser.level}`;
    if (navAvatar) navAvatar.textContent = currentUser.avatar || "🧙‍♂️";
    if (navRankScore) navRankScore.textContent = currentUser.ranked_rating || 1000;
    if (navRankTier) navRankTier.textContent = (currentUser.ranked_tier || "BRONZE I").toUpperCase();
    if (navStreakCount) navStreakCount.textContent = currentUser.current_streak || 0;
    if (heroStreak) heroStreak.textContent = currentUser.current_streak || 0;
  } else {
    if (guestActions) guestActions.style.display = "flex";
    if (userActions) userActions.style.display = "none";
  }
}

// ============================================================================
// AUTH MODAL & FORM HANDLERS
// ============================================================================

function openAuthModal(tab = "login") {
  closeModals();
  switchAuthTab(tab);
  const modal = document.getElementById("auth-modal");
  if (modal) modal.classList.add("active");
}

function switchAuthTab(tab) {
  const tabLogin = document.getElementById("auth-tab-login");
  const tabReg = document.getElementById("auth-tab-register");
  const formLogin = document.getElementById("form-login");
  const formReg = document.getElementById("form-register");
  const loginErr = document.getElementById("auth-login-error");
  const regErr = document.getElementById("auth-register-error");

  if (loginErr) loginErr.style.display = "none";
  if (regErr) regErr.style.display = "none";

  if (tab === "login") {
    tabLogin.classList.add("active");
    tabReg.classList.remove("active");
    formLogin.style.display = "block";
    formReg.style.display = "none";
  } else {
    tabReg.classList.add("active");
    tabLogin.classList.remove("active");
    formReg.style.display = "block";
    formLogin.style.display = "none";
  }
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const identifier = document.getElementById("login-identifier").value;
  const password = document.getElementById("login-password").value;
  const btn = document.getElementById("btn-login-submit");
  const errBox = document.getElementById("auth-login-error");

  btn.disabled = true;
  btn.textContent = "Signing In...";
  if (errBox) errBox.style.display = "none";

  try {
    const res = await apiRequest("/api/auth/login", {
      method: "POST",
      body: { identifier, password }
    });

    localStorage.setItem(AUTH_TOKEN_KEY, res.token);
    currentUser = res.user;
    updateUserNavUI();
    closeModals();
    showToast(`Welcome back, ${currentUser.display_name}!`, "success");
    initSocketConnection();
    refreshAllViews();
  } catch (err) {
    if (errBox) {
      errBox.textContent = err.message || "Invalid credentials.";
      errBox.style.display = "block";
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "SIGN IN";
  }
}

async function handleRegisterSubmit(event) {
  event.preventDefault();
  const username = document.getElementById("reg-username").value;
  const email = document.getElementById("reg-email").value;
  const displayName = document.getElementById("reg-display-name").value;
  const password = document.getElementById("reg-password").value;
  const avatar = document.getElementById("reg-avatar").value || "🧙‍♂️";
  const btn = document.getElementById("btn-register-submit");
  const errBox = document.getElementById("auth-register-error");

  btn.disabled = true;
  btn.textContent = "Creating Account...";
  if (errBox) errBox.style.display = "none";

  try {
    const res = await apiRequest("/api/auth/register", {
      method: "POST",
      body: { username, email, display_name: displayName, password, avatar }
    });

    localStorage.setItem(AUTH_TOKEN_KEY, res.token);
    currentUser = res.user;
    updateUserNavUI();
    closeModals();
    showToast(`Account created! Welcome to Sudoku Quest, ${currentUser.display_name}!`, "success");
    initSocketConnection();
    refreshAllViews();
  } catch (err) {
    if (errBox) {
      errBox.textContent = err.message || "Registration failed.";
      errBox.style.display = "block";
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "CREATE ACCOUNT";
  }
}

async function handleLogout(event) {
  if (event) event.stopPropagation();
  try {
    await apiRequest("/api/auth/logout", { method: "POST" });
  } catch (e) {}

  localStorage.removeItem(AUTH_TOKEN_KEY);
  currentUser = null;
  if (socket) {
    socket.disconnect();
    socket = null;
  }
  updateUserNavUI();
  showToast("Logged out successfully.", "info");
  refreshAllViews();
}

function selectAvatar(emoji) {
  document.getElementById("reg-avatar").value = emoji;
  document.querySelectorAll(".avatar-picker-grid .avatar-opt").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.avatar === emoji);
  });
}

function openAvatarModal() {
  if (!currentUser) {
    openAuthModal("login");
    return;
  }
  closeModals();
  const modal = document.getElementById("avatar-modal");
  if (modal) modal.classList.add("active");
}

async function updateUserAvatar(avatarEmoji) {
  if (!currentUser) return;
  try {
    const res = await apiRequest("/api/auth/profile", {
      method: "PATCH",
      body: { avatar: avatarEmoji }
    });
    currentUser = res.user;
    updateUserNavUI();
    renderProfile();
    closeModals();
    showToast("Avatar updated!", "success");
  } catch (err) {
    showToast("Failed to update avatar.", "error");
  }
}

// ============================================================================
// REAL-TIME SOCKET.IO & MATCHMAKING
// ============================================================================

function initSocketConnection() {
  if (socket && socket.connected) return;

  try {
    socket = io();

    socket.on("connect", () => {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (token) {
        socket.emit("auth", { token });
      }
    });

    socket.on("auth_ok", (data) => {
      console.log("Socket.IO authenticated for user:", data.username);
    });

    socket.on("queue_joined", (data) => {
      const modal = document.getElementById("matchmaking-modal");
      if (modal) modal.classList.add("active");
      const loadingState = document.getElementById("mm-loading-state");
      const foundState = document.getElementById("mm-found-state");
      if (loadingState) loadingState.style.display = "block";
      if (foundState) foundState.style.display = "none";
      startQueueTimer();
    });

    socket.on("queue_left", () => {
      stopQueueTimer();
      closeModals();
    });

    socket.on("match_found", (data) => {
      stopQueueTimer();
      const loadingState = document.getElementById("mm-loading-state");
      const foundState = document.getElementById("mm-found-state");
      if (loadingState) loadingState.style.display = "none";
      if (foundState) foundState.style.display = "block";

      const opp = data.opponent;
      document.getElementById("mm-my-name").textContent = currentUser ? currentUser.display_name : "You";
      document.getElementById("mm-my-avatar").textContent = currentUser ? currentUser.avatar : "🧙‍♂️";
      document.getElementById("mm-my-rating").textContent = currentUser ? currentUser.ranked_rating : 1000;

      document.getElementById("mm-opp-name").textContent = opp.display_name || opp.username;
      document.getElementById("mm-opp-avatar").textContent = opp.avatar || "⚔️";
      document.getElementById("mm-opp-rating").textContent = opp.rating || 1000;
      document.getElementById("mm-match-tier").textContent = `Level ${data.level} ${data.level_name}`;

      // Start countdown
      let count = 3;
      const countEl = document.getElementById("mm-starting-countdown");
      const cInterval = setInterval(() => {
        count--;
        if (countEl) countEl.textContent = `Starting in ${count}s...`;
        if (count <= 0) {
          clearInterval(cInterval);
        }
      }, 1000);
    });

    socket.on("match_start", (data) => {
      closeModals();
      showToast("Ranked Match Started! Solve fast!", "success");
      
      // Initialize ranked multiplayer game state
      gameState.isRanked = true;
      gameState.rankedMatchId = data.match_id;
      gameState.levelNum = data.level;
      gameState.difficulty = data.level_name;
      loadPuzzleToBoard(data.initial_board, data.level_name, data.level, data.clues);
      navigateTo("play");
    });

    socket.on("opponent_progress", (data) => {
      // Live opponent progress indicator (can update subtle progress bar in header)
    });

    socket.on("match_finished", (data) => {
      const myResult = (data.winner_id === (currentUser ? currentUser.id : null))
        ? data.p1_result
        : data.p2_result;

      showRankedResultModal(myResult);
      fetchCurrentUser();
    });

  } catch (err) {
    console.warn("Socket.IO client unavailable:", err);
  }
}

function openRankedMatchmaking() {
  if (!currentUser) {
    showToast("Please Sign In to compete in Ranked Mode.", "info");
    openAuthModal("login");
    return;
  }

  if (!socket || !socket.connected) {
    initSocketConnection();
  }

  const findRatingEl = document.getElementById("mm-user-rating-find");
  if (findRatingEl) findRatingEl.textContent = currentUser.ranked_rating || 1000;

  socket.emit("join_ranked_queue", {
    token: localStorage.getItem(AUTH_TOKEN_KEY)
  });
}

function leaveRankedQueue() {
  if (socket) {
    socket.emit("leave_ranked_queue");
  }
  stopQueueTimer();
  closeModals();
}

function startQueueTimer() {
  stopQueueTimer();
  mmTimerSeconds = 0;
  const timerEl = document.getElementById("mm-queue-timer");
  if (timerEl) timerEl.textContent = "Searching: 00:00";

  mmTimerInterval = setInterval(() => {
    mmTimerSeconds++;
    const mins = String(Math.floor(mmTimerSeconds / 60)).padStart(2, "0");
    const secs = String(mmTimerSeconds % 60).padStart(2, "0");
    if (timerEl) timerEl.textContent = `Searching: ${mins}:${secs}`;
  }, 1000);
}

function stopQueueTimer() {
  if (mmTimerInterval) {
    clearInterval(mmTimerInterval);
    mmTimerInterval = null;
  }
}

function showRankedResultModal(result) {
  closeModals();
  const modal = document.getElementById("ranked-result-modal");
  if (!modal) return;

  const iconEl = document.getElementById("r-res-icon");
  const titleEl = document.getElementById("r-res-title");
  const subEl = document.getElementById("r-res-subtitle");
  const deltaVal = document.getElementById("r-delta-val");
  const newRating = document.getElementById("r-new-rating");
  const myTime = document.getElementById("r-stat-mytime");
  const xpVal = document.getElementById("r-stat-xp");

  if (result.is_winner) {
    iconEl.textContent = "🏆";
    titleEl.textContent = "VICTORY";
    subEl.textContent = "You outplayed your opponent in the grid!";
    deltaVal.textContent = `+${result.rating_delta}`;
    deltaVal.className = "r-delta-val text-green";
  } else {
    iconEl.textContent = "⚔️";
    titleEl.textContent = "DEFEAT";
    subEl.textContent = "Close match! Review your solve and queue again.";
    deltaVal.textContent = `${result.rating_delta}`;
    deltaVal.className = "r-delta-val text-red";
  }

  newRating.textContent = `New Rating: ${result.new_rating} (${result.new_tier})`;
  const mins = String(Math.floor(result.time_seconds / 60)).padStart(2, "0");
  const secs = String(result.time_seconds % 60).padStart(2, "0");
  myTime.textContent = `${mins}:${secs}`;
  xpVal.textContent = `+${result.xp_earned} XP`;

  modal.classList.add("active");
}

// ============================================================================
// AUTHORITATIVE GAMEPLAY LIFECYCLE
// ============================================================================

async function startQuickGame() {
  await startNewGame(currentUser ? currentUser.level : 4, "medium");
  navigateTo("play");
}

async function startNewGame(levelNum = 4, difficulty = "medium", isDaily = false) {
  try {
    const res = await apiRequest("/api/games", {
      method: "POST",
      body: { level_num: levelNum, difficulty, is_daily: isDaily }
    });

    gameState.gameId = res.game_id;
    gameState.isDaily = isDaily;
    gameState.isRanked = false;
    gameState.levelNum = res.level_num;
    gameState.difficulty = res.difficulty;
    
    loadPuzzleToBoard(res.initial_board, res.level_name, res.level_num, res.clues, res.xp);
  } catch (err) {
    showToast("Failed to initialize game session.", "error");
  }
}

async function startDailyChallenge() {
  await startNewGame(4, "medium", true);
  navigateTo("play");
}

function loadPuzzleToBoard(initialBoardStr, levelName, levelNum, cluesCount, xpReward = 100) {
  stopGameTimer();
  
  gameState.initialBoard = initialBoardStr.split("");
  gameState.currentBoard = initialBoardStr.split("");
  gameState.notes = Array(81).fill(null).map(() => new Set());
  gameState.selectedCell = null;
  gameState.mistakes = 0;
  gameState.hintsUsed = 0;
  gameState.hintsRemaining = 3;
  gameState.isCompleted = false;
  gameState.isNotesMode = false;
  gameState.timerSeconds = 0;
  gameState.history = [];

  // Update UI Elements
  document.getElementById("game-level-chip").textContent = `Level ${levelNum} — ${levelName}`;
  document.getElementById("game-clues-info").textContent = `${cluesCount} Clues`;
  document.getElementById("active-xp-val").textContent = `+${xpReward}`;
  document.getElementById("hints-remaining-count").textContent = "3";
  document.getElementById("notes-status-badge").textContent = "OFF";
  document.getElementById("mistake-hearts").textContent = "❤️❤️❤️";

  renderBoard();
  startGameTimer();
  updateNumpadRemainingCounts();
}

function renderBoard() {
  const gridEl = document.getElementById("sudoku-grid");
  if (!gridEl) return;
  gridEl.innerHTML = "";

  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      const idx = r * 9 + c;
      const cell = document.createElement("div");
      cell.className = "grid-cell";
      cell.dataset.index = idx;
      cell.dataset.row = r;
      cell.dataset.col = c;

      const val = gameState.currentBoard[idx];
      const isGiven = (gameState.initialBoard[idx] !== ".");

      if (isGiven) {
        cell.classList.add("given");
        cell.textContent = val;
      } else if (val !== ".") {
        cell.classList.add("user-filled");
        cell.textContent = val;
      } else {
        // Render pencil notes if any
        const notes = gameState.notes[idx];
        if (notes && notes.size > 0) {
          const notesGrid = document.createElement("div");
          notesGrid.className = "cell-notes-grid";
          for (let n = 1; n <= 9; n++) {
            const noteSpan = document.createElement("span");
            noteSpan.className = "note-digit";
            noteSpan.textContent = notes.has(n) ? n : "";
            notesGrid.appendChild(noteSpan);
          }
          cell.appendChild(notesGrid);
        }
      }

      cell.onclick = () => selectCell(idx);
      gridEl.appendChild(cell);
    }
  }

  highlightSelectedCell();
}

function selectCell(idx) {
  gameState.selectedCell = idx;
  highlightSelectedCell();
}

function highlightSelectedCell() {
  const cells = document.querySelectorAll(".grid-cell");
  const selIdx = gameState.selectedCell;

  cells.forEach(c => {
    c.classList.remove("selected", "same-digit", "related");
  });

  if (selIdx === null) return;

  const selRow = Math.floor(selIdx / 9);
  const selCol = selIdx % 9;
  const selVal = gameState.currentBoard[selIdx];

  cells.forEach(cell => {
    const idx = parseInt(cell.dataset.index);
    const r = parseInt(cell.dataset.row);
    const c = parseInt(cell.dataset.col);
    const val = gameState.currentBoard[idx];

    if (idx === selIdx) {
      cell.classList.add("selected");
    } else if (selVal !== "." && val === selVal) {
      cell.classList.add("same-digit");
    } else if (r === selRow || c === selCol || (Math.floor(r / 3) === Math.floor(selRow / 3) && Math.floor(c / 3) === Math.floor(selCol / 3))) {
      cell.classList.add("related");
    }
  });
}

async function inputNumber(num) {
  const selIdx = gameState.selectedCell;
  if (selIdx === null || gameState.isCompleted) return;

  // Cannot modify initial given clue cells
  if (gameState.initialBoard[selIdx] !== ".") return;

  if (gameState.isNotesMode) {
    const notes = gameState.notes[selIdx];
    if (notes.has(num)) {
      notes.delete(num);
    } else {
      notes.add(num);
    }
    renderBoard();
    return;
  }

  // Authoritative server move validation
  try {
    const res = await apiRequest(`/api/games/${gameState.gameId}/move`, {
      method: "POST",
      body: { cell_index: selIdx, value: num }
    });

    if (res.is_correct) {
      gameState.currentBoard[selIdx] = String(num);
      gameState.notes[selIdx].clear();
      renderBoard();
      updateNumpadRemainingCounts();

      // Send live progress if in ranked match
      if (gameState.isRanked && socket) {
        const solvedCount = gameState.currentBoard.filter(ch => ch !== ".").length;
        const progressPct = Math.round((solvedCount / 81) * 100);
        socket.emit("player_progress", {
          match_id: gameState.rankedMatchId,
          progress_pct: progressPct,
          mistakes: gameState.mistakes
        });
      }

      // Check if board full -> complete game
      if (!gameState.currentBoard.includes(".")) {
        handleGameWin();
      }
    } else {
      gameState.mistakes = res.mistakes;
      updateMistakesUI();

      const cellEl = document.querySelector(`.grid-cell[data-index="${selIdx}"]`);
      if (cellEl) {
        cellEl.classList.add("error-pulse");
        setTimeout(() => cellEl.classList.remove("error-pulse"), 600);
      }

      if (res.game_over) {
        handleGameOver();
      }
    }
  } catch (err) {
    showToast("Move validation error.", "error");
  }
}

function updateMistakesUI() {
  const heartsEl = document.getElementById("mistake-hearts");
  if (!heartsEl) return;
  const rem = Math.max(0, 3 - gameState.mistakes);
  heartsEl.textContent = "❤️".repeat(rem) + "🖤".repeat(3 - rem);
}

async function handleHint() {
  if (gameState.hintsRemaining <= 0 || gameState.isCompleted) {
    showToast("No hints remaining for this puzzle!", "info");
    return;
  }

  try {
    const res = await apiRequest(`/api/games/${gameState.gameId}/hint`, { method: "POST" });
    gameState.hintsRemaining--;
    document.getElementById("hints-remaining-count").textContent = gameState.hintsRemaining;

    const idx = res.cell_index;
    gameState.currentBoard[idx] = String(res.value);
    gameState.notes[idx].clear();
    gameState.selectedCell = idx;
    renderBoard();
    updateNumpadRemainingCounts();

    showToast(`Hint: Row ${res.row + 1}, Col ${res.col + 1} is ${res.value}`, "info");

    if (!gameState.currentBoard.includes(".")) {
      handleGameWin();
    }
  } catch (err) {
    showToast("Failed to fetch hint.", "error");
  }
}

function handleErase() {
  const selIdx = gameState.selectedCell;
  if (selIdx === null || gameState.initialBoard[selIdx] !== "." || gameState.isCompleted) return;

  gameState.currentBoard[selIdx] = ".";
  gameState.notes[selIdx].clear();
  renderBoard();
  updateNumpadRemainingCounts();
}

function handleUndo() {
  showToast("Undone last action", "info");
}

function toggleNotesMode() {
  gameState.isNotesMode = !gameState.isNotesMode;
  const badge = document.getElementById("notes-status-badge");
  if (badge) badge.textContent = gameState.isNotesMode ? "ON" : "OFF";
}

function updateNumpadRemainingCounts() {
  for (let n = 1; n <= 9; n++) {
    const count = gameState.currentBoard.filter(ch => ch === String(n)).length;
    const rem = 9 - count;
    const span = document.getElementById(`rem-${n}`);
    if (span) span.textContent = rem > 0 ? rem : "✓";
  }
}

async function handleGameWin() {
  stopGameTimer();
  gameState.isCompleted = true;

  if (gameState.isRanked && socket) {
    socket.emit("player_complete", {
      match_id: gameState.rankedMatchId,
      board: gameState.currentBoard.join(""),
      elapsed_seconds: gameState.timerSeconds,
      mistakes: gameState.mistakes
    });
    return;
  }

  try {
    const res = await apiRequest(`/api/games/${gameState.gameId}/complete`, {
      method: "POST",
      body: { board: gameState.currentBoard.join("") }
    });

    // Update user profile from backend
    if (res.user) {
      currentUser = res.user;
      updateUserNavUI();
    }

    // Show celebratory modals
    showWinModal(res);

    if (res.achievements_unlocked && res.achievements_unlocked.length > 0) {
      res.achievements_unlocked.forEach(ach => {
        setTimeout(() => showAchievementUnlockedModal(ach), 800);
      });
    }
  } catch (err) {
    showToast("Failed to finalize game session.", "error");
  }
}

function showWinModal(res) {
  closeModals();
  const modal = document.getElementById("win-modal");
  if (!modal) return;

  const mins = String(Math.floor(res.elapsed_seconds / 60)).padStart(2, "0");
  const secs = String(res.elapsed_seconds % 60).padStart(2, "0");

  document.getElementById("win-time").textContent = `${mins}:${secs}`;
  document.getElementById("win-diff").textContent = `Level ${gameState.levelNum} ${gameState.difficulty}`;
  document.getElementById("win-mistakes").textContent = res.mistakes;
  document.getElementById("win-xp").textContent = `+${res.xp_earned} XP`;

  modal.classList.add("active");
}

function handleGameOver() {
  stopGameTimer();
  gameState.isCompleted = true;
  const modal = document.getElementById("lose-modal");
  if (modal) modal.classList.add("active");
}

function restartCurrentPuzzle() {
  closeModals();
  gameState.currentBoard = [...gameState.initialBoard];
  gameState.mistakes = 0;
  gameState.isCompleted = false;
  updateMistakesUI();
  renderBoard();
  startGameTimer();
}

function playHighestUnlockedLevel() {
  closeModals();
  const nextLvl = Math.min(10, (gameState.levelNum || 1) + 1);
  startNewGame(nextLvl);
}

// Timer Logic
function startGameTimer() {
  stopGameTimer();
  const timerEl = document.getElementById("game-timer");
  gameState.timerInterval = setInterval(() => {
    gameState.timerSeconds++;
    const mins = String(Math.floor(gameState.timerSeconds / 60)).padStart(2, "0");
    const secs = String(gameState.timerSeconds % 60).padStart(2, "0");
    if (timerEl) timerEl.textContent = `${mins}:${secs}`;
  }, 1000);
}

function stopGameTimer() {
  if (gameState.timerInterval) {
    clearInterval(gameState.timerInterval);
    gameState.timerInterval = null;
  }
}

// ============================================================================
// ACHIEVEMENTS ENGINE & UI
// ============================================================================

async function fetchAchievements() {
  try {
    const masterRes = await apiRequest("/api/achievements");
    masterAchievements = masterRes.achievements || [];

    const userRes = await apiRequest("/api/achievements/me");
    userUnlockedAchievements = new Set((userRes.unlocked || []).map(u => u.code));

    renderAchievementsView();
    renderHomeAchievementsPreview();
  } catch (err) {
    console.error("Failed to load achievements:", err);
  }
}

function filterAchievements(category) {
  activeCategoryFilter = category;
  document.querySelectorAll(".ach-tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.cat === category);
  });
  renderAchievementsView();
}

function renderAchievementsView() {
  const grid = document.getElementById("achievements-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const filtered = masterAchievements.filter(a => {
    if (activeCategoryFilter === "all") return true;
    return a.cat === activeCategoryFilter;
  });

  const total = masterAchievements.length;
  const unlockedCount = userUnlockedAchievements.size;
  const pct = Math.round((unlockedCount / total) * 100);

  const countEl = document.getElementById("ach-unlocked-count");
  const pctEl = document.getElementById("ach-pct-badge");
  const fillEl = document.getElementById("ach-fill-bar");

  if (countEl) countEl.textContent = `Unlocked: ${unlockedCount} / ${total}`;
  if (pctEl) pctEl.textContent = `${pct}%`;
  if (fillEl) fillEl.style.width = `${pct}%`;

  filtered.forEach(ach => {
    const isUnlocked = userUnlockedAchievements.has(ach.code);
    const card = document.createElement("div");
    card.className = `achievement-card glass-card ${isUnlocked ? "unlocked" : "locked"}`;

    card.innerHTML = `
      <div class="ach-icon">${isUnlocked ? ach.icon : "🔒"}</div>
      <div class="ach-info">
        <h4 class="ach-title">${ach.title}</h4>
        <p class="ach-desc">${ach.desc}</p>
        <div class="ach-footer">
          <span class="ach-status ${isUnlocked ? "text-green" : "text-muted"}">${isUnlocked ? "✓ UNLOCKED" : "🔒 LOCKED"}</span>
          <span class="ach-xp text-gold">+${ach.xp} XP</span>
        </div>
      </div>
    `;

    grid.appendChild(card);
  });
}

function renderHomeAchievementsPreview() {
  const container = document.getElementById("home-ach-preview-grid");
  if (!container) return;
  container.innerHTML = "";

  const unlockedCodes = Array.from(userUnlockedAchievements);
  const displayList = masterAchievements.filter(a => unlockedCodes.includes(a.code)).slice(0, 3);

  if (displayList.length === 0) {
    container.innerHTML = `
      <div class="empty-state-card w-full" style="grid-column: 1 / -1; margin: 0;">
        <div class="empty-state-icon">🏆</div>
        <h4 class="empty-state-title">No Achievements Unlocked Yet</h4>
        <p class="empty-state-desc">Solve your first Sudoku puzzle to unlock your first trophy & earn XP rewards!</p>
      </div>
    `;
    return;
  }

  displayList.forEach(ach => {
    const chip = document.createElement("div");
    chip.className = "home-ach-chip glass-card unlocked";
    chip.innerHTML = `
      <span class="h-ach-icon">${ach.icon}</span>
      <div class="h-ach-meta">
        <strong>${ach.title}</strong>
        <span>+${ach.xp} XP</span>
      </div>
    `;
    container.appendChild(chip);
  });
}

function showAchievementUnlockedModal(ach) {
  closeModals();
  const modal = document.getElementById("achievement-unlocked-modal");
  if (!modal) return;

  document.getElementById("ach-popup-icon").textContent = ach.icon || "🏆";
  document.getElementById("ach-popup-title").textContent = ach.title;
  document.getElementById("ach-popup-desc").textContent = ach.desc;
  document.getElementById("ach-popup-reward").textContent = `+${ach.xp} XP`;

  modal.classList.add("active");
  userUnlockedAchievements.add(ach.code);
  renderAchievementsView();
  renderHomeAchievementsPreview();
}

// ============================================================================
// LEADERBOARD & STATISTICS
// ============================================================================

async function fetchLeaderboard() {
  try {
    const res = await apiRequest("/api/leaderboard");
    const tbody = document.getElementById("leaderboard-tbody");
    const emptyState = document.getElementById("leaderboard-empty-state");
    const tableEl = document.getElementById("leaderboard-table");

    if (!tbody) return;
    tbody.innerHTML = "";

    const list = res.leaderboard || [];
    if (list.length === 0) {
      if (emptyState) emptyState.style.display = "block";
      if (tableEl) tableEl.style.display = "none";
      return;
    }

    if (emptyState) emptyState.style.display = "none";
    if (tableEl) tableEl.style.display = "table";

    list.forEach(p => {
      const tr = document.createElement("tr");
      const isMe = currentUser && currentUser.id === p.user_id;
      if (isMe) tr.className = "my-row";

      tr.innerHTML = `
        <td class="td-rank">#${p.rank}</td>
        <td class="td-player">
          <span class="player-avatar">${p.avatar}</span>
          <span class="player-name">${p.display_name || p.username} ${isMe ? "(You)" : ""}</span>
        </td>
        <td class="td-rating text-gold">${p.rating}</td>
        <td><span class="tier-badge ${p.tier.toLowerCase()}">${p.tier}</span></td>
        <td>${p.wins}</td>
        <td>${p.win_rate}</td>
        <td class="text-cyan">${p.xp} XP</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load leaderboard:", err);
  }
}

async function fetchStatistics() {
  try {
    const res = await apiRequest("/api/stats");
    const uStats = res.user_stats;
    const emptyState = document.getElementById("stats-empty-state");
    const content = document.getElementById("stats-content-wrapper");

    if (!uStats || uStats.total_games === 0) {
      if (emptyState) emptyState.style.display = "block";
      if (content) content.style.display = "none";
      return;
    }

    if (emptyState) emptyState.style.display = "none";
    if (content) content.style.display = "block";

    document.getElementById("stat-puzzles-solved").textContent = uStats.completed_games;
    document.getElementById("stat-current-streak").textContent = currentUser ? currentUser.current_streak : 0;
    document.getElementById("stat-best-streak").textContent = currentUser ? currentUser.best_streak : 0;
    
    const mins = String(Math.floor(uStats.avg_time_seconds / 60)).padStart(2, "0");
    const secs = String(uStats.avg_time_seconds % 60).padStart(2, "0");
    document.getElementById("stat-avg-time").textContent = `${mins}:${secs}`;

    const bMins = String(Math.floor(uStats.best_time_seconds / 60)).padStart(2, "0");
    const bSecs = String(uStats.best_time_seconds % 60).padStart(2, "0");
    document.getElementById("stat-best-time").textContent = uStats.best_time_seconds > 0 ? `${bMins}:${bSecs}` : "--:--";

    const accuracy = uStats.total_games > 0 ? Math.round((uStats.completed_games / uStats.total_games) * 100) : 100;
    document.getElementById("stat-accuracy").textContent = `${accuracy}%`;
    document.getElementById("stat-total-mistakes").textContent = uStats.total_mistakes;
    document.getElementById("stat-hints-used").textContent = uStats.total_hints;

    // Quick Stats Home update
    const qsSolved = document.getElementById("qs-solved");
    const qsWinrate = document.getElementById("qs-winrate");
    const qsRank = document.getElementById("qs-rank");
    const qsBest = document.getElementById("qs-best-time");

    if (qsSolved) qsSolved.textContent = uStats.completed_games;
    if (qsWinrate) qsWinrate.textContent = `${accuracy}%`;
    if (qsRank) qsRank.textContent = currentUser ? currentUser.ranked_rating : 1000;
    if (qsBest) qsBest.textContent = uStats.best_time_seconds > 0 ? `${bMins}:${bSecs}` : "--:--";
  } catch (err) {
    console.error("Failed to load statistics:", err);
  }
}

function renderProfile() {
  if (!currentUser) {
    document.getElementById("profile-username-display").textContent = "Guest Player";
    document.getElementById("profile-avatar-emoji").textContent = "🧙‍♂️";
    document.getElementById("profile-tier-badge").textContent = "Level 1 Beginner";
    document.getElementById("profile-current-lvl-text").textContent = "Level 1 Beginner";
    document.getElementById("profile-xp-text").textContent = "0 / 100 XP";
    document.getElementById("profile-xp-fill").style.width = "0%";
    return;
  }

  document.getElementById("profile-username-display").textContent = currentUser.display_name || currentUser.username;
  document.getElementById("profile-avatar-emoji").textContent = currentUser.avatar || "🧙‍♂️";
  document.getElementById("profile-tier-badge").textContent = `Level ${currentUser.level}`;
  document.getElementById("profile-current-lvl-text").textContent = `Level ${currentUser.level}`;
  document.getElementById("profile-rank-val").textContent = currentUser.ranked_rating;
  document.getElementById("profile-streak-val").textContent = currentUser.current_streak;
  document.getElementById("profile-puzzles-val").textContent = currentUser.puzzles_solved;

  document.getElementById("rc-matches").textContent = (currentUser.ranked_wins || 0) + (currentUser.ranked_losses || 0);
  document.getElementById("rc-wins").textContent = currentUser.ranked_wins || 0;
  document.getElementById("rc-losses").textContent = currentUser.ranked_losses || 0;
  const tot = (currentUser.ranked_wins || 0) + (currentUser.ranked_losses || 0);
  document.getElementById("rc-winrate").textContent = tot > 0 ? `${((currentUser.ranked_wins / tot) * 100).toFixed(1)}%` : "0.0%";
}

// ============================================================================
// NAVIGATION & MODALS
// ============================================================================

function navigateTo(viewName) {
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(btn => btn.classList.remove("active"));

  const targetView = document.getElementById(`view-${viewName}`);
  const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);

  if (targetView) targetView.classList.add("active");
  if (targetNav) targetNav.classList.add("active");

  const mobileNav = document.getElementById("nav-menu");
  if (mobileNav) mobileNav.classList.remove("mobile-open");

  if (viewName === "achievements") fetchAchievements();
  if (viewName === "ranked") fetchLeaderboard();
  if (viewName === "stats") fetchStatistics();
  if (viewName === "profile") renderProfile();
}

function toggleMobileMenu() {
  const menu = document.getElementById("nav-menu");
  if (menu) menu.classList.toggle("mobile-open");
}

function closeModals() {
  document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("active"));
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("fade-out");
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

function refreshAllViews() {
  fetchAchievements();
  fetchLeaderboard();
  fetchStatistics();
  renderProfile();
}

// Keyboard Controls
window.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT") return;

  if (e.key >= "1" && e.key <= "9") {
    inputNumber(parseInt(e.key));
  } else if (e.key === "Backspace" || e.key === "Delete") {
    handleErase();
  } else if (e.key === "n" || e.key === "N") {
    toggleNotesMode();
  } else if (e.key === "h" || e.key === "H") {
    handleHint();
  } else if (e.key === "u" || e.key === "U") {
    handleUndo();
  } else if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "w", "a", "s", "d"].includes(e.key)) {
    handleArrowKeyMove(e.key);
  }
});

function handleArrowKeyMove(key) {
  if (gameState.selectedCell === null) {
    selectCell(0);
    return;
  }
  let r = Math.floor(gameState.selectedCell / 9);
  let c = gameState.selectedCell % 9;

  if (key === "ArrowUp" || key === "w") r = (r - 1 + 9) % 9;
  if (key === "ArrowDown" || key === "s") r = (r + 1) % 9;
  if (key === "ArrowLeft" || key === "a") c = (c - 1 + 9) % 9;
  if (key === "ArrowRight" || key === "d") c = (c + 1) % 9;

  selectCell(r * 9 + c);
}

const PROGRESSION_LEVELS = [
  { level: 1, name: "Beginner", diff: "very easy", key: "beginner", clues: "45-50", xp: 25, time: "3-5 min", color: "#10b981", icon: "🌱", desc: "Gentle introduction to 9x9 logic." },
  { level: 2, name: "Novice", diff: "easy", key: "novice", clues: "40-45", xp: 50, time: "5-8 min", color: "#06b6d4", icon: "🔹", desc: "Build foundational deduction techniques." },
  { level: 3, name: "Easy Master", diff: "easy+", key: "easy", clues: "36-40", xp: 100, time: "8-10 min", color: "#3b82f6", icon: "⚡", desc: "Solid puzzles requiring clean naked singles." },
  { level: 4, name: "Medium Master", diff: "standard", key: "medium", clues: "32-36", xp: 150, time: "10-15 min", color: "#6366f1", icon: "🔵", desc: "Standard tournament-style Sudoku grid." },
  { level: 5, name: "Advanced", diff: "medium+", key: "advanced", clues: "28-32", xp: 200, time: "15-20 min", color: "#8b5cf6", icon: "🟣", desc: "Hidden pairs and box-line reductions." },
  { level: 6, name: "Hard Master", diff: "challenging", key: "hard", clues: "24-28", xp: 250, time: "20-25 min", color: "#ec4899", icon: "🔥", desc: "Complex pointing pairs and multi-branch logic." },
  { level: 7, name: "Master", diff: "expert", key: "master", clues: "22-24", xp: 350, time: "25-30 min", color: "#f59e0b", icon: "👑", desc: "X-Wing, Swordfish, and advanced patterns." },
  { level: 8, name: "Expert", diff: "master", key: "expert", clues: "20-22", xp: 400, time: "30-40 min", color: "#f97316", icon: "💎", desc: "Deep multi-step candidate elimination." },
  { level: 9, name: "Grandmaster", diff: "extreme", key: "grandmaster", clues: "18-20", xp: 450, time: "40-50 min", color: "#ef4444", icon: "💠", desc: "Elite logic requiring extreme concentration." },
  { level: 10, name: "Legend", diff: "impossible", key: "legend", clues: "17", xp: 500, time: "50-60 min", color: "#eab308", icon: "🏆", desc: "Theoretical limit of minimal 17-clue Sudoku." }
];

function populateLevelsUI() {
  // Populate Home Page Cards Grid
  const grid = document.getElementById("level-cards-grid");
  if (grid) {
    grid.innerHTML = "";
    PROGRESSION_LEVELS.forEach(lvl => {
      const card = document.createElement("div");
      card.className = "level-card glass-card";
      card.onclick = () => {
        startNewGame(lvl.level, lvl.key);
        navigateTo("play");
      };

      card.innerHTML = `
        <div class="level-card-top">
          <span class="level-number-badge" style="background: ${lvl.color}22; color: ${lvl.color}; border: 1px solid ${lvl.color}44;">LEVEL ${lvl.level}</span>
          <span class="level-icon">${lvl.icon}</span>
        </div>
        <h3 class="level-card-title">${lvl.name}</h3>
        <p class="level-card-desc">${lvl.desc}</p>
        <div class="level-card-metrics">
          <span>⏱️ ${lvl.time}</span>
          <span>🧩 ${lvl.clues} Clues</span>
        </div>
        <div class="level-card-footer">
          <span class="level-xp-reward text-gold">+${lvl.xp} XP</span>
          <button class="btn btn-primary btn-sm">PLAY →</button>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  // Populate Play View Selector
  const selector = document.getElementById("difficulty-selector");
  if (selector) {
    selector.innerHTML = "";
    PROGRESSION_LEVELS.forEach(lvl => {
      const opt = document.createElement("option");
      opt.value = lvl.level;
      opt.textContent = `Level ${lvl.level} — ${lvl.name} (+${lvl.xp} XP)`;
      selector.appendChild(opt);
    });
  }

  // Populate Roadmap
  const track = document.getElementById("roadmap-track-container");
  if (track) {
    track.innerHTML = "";
    PROGRESSION_LEVELS.forEach((lvl, idx) => {
      const node = document.createElement("div");
      const userLvl = currentUser ? currentUser.level : 1;
      const isUnlocked = lvl.level <= userLvl;
      const isCurrent = lvl.level === userLvl;

      node.className = `roadmap-node ${isCurrent ? "current" : (isUnlocked ? "unlocked" : "locked")}`;
      node.onclick = () => {
        startNewGame(lvl.level, lvl.key);
        navigateTo("play");
      };

      node.innerHTML = `
        <div class="rm-node-circle" style="border-color: ${lvl.color};">
          <span>${lvl.icon}</span>
        </div>
        <div class="rm-node-meta">
          <span class="rm-lvl">Lvl ${lvl.level}</span>
          <strong class="rm-name">${lvl.name}</strong>
        </div>
      `;
      track.appendChild(node);
    });
  }
}

function changeGameLevel(levelVal) {
  const lvlNum = parseInt(levelVal);
  const lvlConf = PROGRESSION_LEVELS.find(l => l.level === lvlNum);
  if (lvlConf) {
    startNewGame(lvlConf.level, lvlConf.key);
  }
}

// Initial Bootstrap
document.addEventListener("DOMContentLoaded", async () => {
  populateLevelsUI();
  await fetchCurrentUser();
  populateLevelsUI(); // Refresh roadmap with user level
  await fetchAchievements();
  await fetchLeaderboard();
  await fetchStatistics();
  renderProfile();
});

