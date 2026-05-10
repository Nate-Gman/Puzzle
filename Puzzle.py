import webbrowser
import os
import tempfile
import atexit

# ==============================================
# Puzzle.py – Grok Image Puzzle Game (Python launcher)
# 
# How to use:
#   1. Save this entire code as Puzzle.py
#   2. Run: python Puzzle.py
#   3. Your browser will open automatically with the full puzzle game
# 
# Features (exactly as requested):
# • Import any image URL from the internet
# • Custom rows × columns (2–8)
# • Crops image into that many rectangular pieces
# • Pieces start randomly scattered
# • Click + drag to move pieces
# • Auto-snap when close to correct position
# • Help button (shows original image + faint overlay)
# • Shuffle, Reset, Win detection + confetti
# • 100% self-contained – no installation needed
# ==============================================

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grok Puzzle Game • Drag & Drop Image Puzzle</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        body {
            font-family: 'Inter', system-ui, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0f172a, #1e2937);
            color: #f1f5f9;
            text-align: center;
        }
        
        h1 {
            margin: 0 0 10px 0;
            font-size: 2.2rem;
            font-weight: 600;
            background: linear-gradient(90deg, #22d3ee, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            color: #64748b;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }
        
        .controls {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(12px);
            max-width: 720px;
            margin: 0 auto 30px;
            padding: 20px 30px;
            border-radius: 20px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        input[type="text"] {
            padding: 14px 18px;
            border-radius: 12px;
            border: none;
            background: #1e2937;
            color: #f1f5f9;
            font-size: 1rem;
            width: 380px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }
        
        input[type="number"] {
            padding: 14px 12px;
            border-radius: 12px;
            border: none;
            background: #1e2937;
            color: #f1f5f9;
            font-size: 1rem;
            width: 80px;
            text-align: center;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }
        
        label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            color: #cbd5e1;
        }
        
        button {
            padding: 14px 24px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            background: linear-gradient(90deg, #22d3ee, #a78bfa);
            color: #0f172a;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(163, 230, 77, 0.3);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(163, 230, 77, 0.4);
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .secondary {
            background: #334155;
            color: #f1f5f9;
        }
        
        canvas {
            border: 8px solid #1e2937;
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.4);
            background: #0f172a;
            max-width: 100%;
            height: auto;
        }
        
        #message {
            margin-top: 20px;
            font-size: 1.5rem;
            font-weight: 600;
            min-height: 2.2em;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: #1e2937;
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.5);
            max-width: 90%;
            max-height: 85%;
            text-align: center;
        }
        
        .modal-content img {
            max-width: 100%;
            max-height: 70vh;
            border-radius: 16px;
            border: 6px solid #334155;
        }
        
        .info {
            font-size: 0.95rem;
            color: #64748b;
            max-width: 720px;
            margin: 15px auto 0;
        }
    </style>
</head>
<body>
    <h1>🧩 Grok Puzzle Game</h1>
    <p class="subtitle">Import any image from the internet • Choose your grid size • Drag &amp; drop the pieces</p>
    
    <div class="controls">
        <label>
            Image URL
            <input type="text" id="imgUrl" value="https://picsum.photos/id/1015/1200/800" placeholder="https://...">
        </label>
        
        <label>
            Rows
            <input type="number" id="rows" value="4" min="2" max="10">
        </label>
        
        <label>
            Columns
            <input type="number" id="cols" value="4" min="2" max="10">
        </label>
        
        <button onclick="createPuzzle()">🚀 Generate Puzzle</button>
        <button onclick="shufflePieces()" class="secondary">🔀 Shuffle</button>
        <button onclick="toggleHelp()" class="secondary">❔ Help (Original Image)</button>
        <button onclick="resetPuzzle()" class="secondary">⟳ Reset</button>
    </div>
    
    <canvas id="canvas" width="1100" height="700"></canvas>
    
    <div id="message"></div>
    
    <div class="info">
        <strong>How to play:</strong> Click and drag any puzzle piece. Drop it near its correct spot — it will snap automatically.<br>
        Custom number of pieces = Rows × Columns. Works with any public image URL (picsum, imgur, etc.).
    </div>
    
    <!-- Help Modal -->
    <div id="help-modal" class="modal">
        <div class="modal-content">
            <h2 style="margin: 0 0 15px 0; color: #22d3ee;">Original Image</h2>
            <img id="original-image" alt="Original image">
            <br><br>
            <button onclick="toggleHelp()" style="background:#334155; color:#f1f5f9; padding:12px 32px;">Close</button>
        </div>
    </div>
    
    <script>
        let canvas, ctx;
        let sourceImg = new Image();
        let pieces = [];
        let draggedPiece = null;
        let offsetX = 0, offsetY = 0;
        let puzzleX = 60, puzzleY = 60;
        let puzzleWidth = 0, puzzleHeight = 0;
        let pieceW = 0, pieceH = 0;
        let rows = 4, cols = 4;
        let showHelpOverlay = false;
        let gameReady = false;
        
        function createPuzzle() {
            const url = document.getElementById('imgUrl').value.trim();
            if (!url) {
                showMessage('⚠️ Please enter a valid image URL', true);
                return;
            }
            
            rows = parseInt(document.getElementById('rows').value);
            cols = parseInt(document.getElementById('cols').value);
            
            if (rows < 2 || cols < 2 || rows > 10 || cols > 10) {
                showMessage('Rows and columns must be between 2–10', true);
                return;
            }
            
            showMessage('Loading image…');
            
            sourceImg = new Image();
            sourceImg.crossOrigin = "anonymous";
            sourceImg.onload = initializeGame;
            sourceImg.onerror = () => {
                showMessage('❌ Could not load image. Try a public URL like picsum.photos', true);
            };
            sourceImg.src = url;
        }
        
        function initializeGame() {
            canvas = document.getElementById('canvas');
            ctx = canvas.getContext('2d');
            
            const MAX_PUZZLE_SIZE = 580;
            const scale = Math.min(MAX_PUZZLE_SIZE / sourceImg.width, MAX_PUZZLE_SIZE / sourceImg.height);
            puzzleWidth = Math.floor(sourceImg.width * scale);
            puzzleHeight = Math.floor(sourceImg.height * scale);
            
            canvas.width = puzzleWidth + 480;
            canvas.height = Math.max(puzzleHeight + 120, 680);
            
            pieceW = puzzleWidth / cols;
            pieceH = puzzleHeight / rows;
            
            pieces = [];
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    const piece = {
                        row: r,
                        col: c,
                        currX: 0,
                        currY: 0,
                        correctX: puzzleX + c * pieceW,
                        correctY: puzzleY + r * pieceH,
                        width: pieceW,
                        height: pieceH
                    };
                    pieces.push(piece);
                }
            }
            
            shufflePieces(false);
            
            if (!gameReady) {
                // Mouse events
                canvas.addEventListener('mousedown', onMouseDown);
                canvas.addEventListener('mousemove', onMouseMove);
                canvas.addEventListener('mouseup', onMouseUp);
                canvas.addEventListener('mouseleave', onMouseUp);
                // Touch events for mobile
                canvas.addEventListener('touchstart', onTouchStart, {passive: false});
                canvas.addEventListener('touchmove', onTouchMove, {passive: false});
                canvas.addEventListener('touchend', onTouchEnd);
                canvas.addEventListener('touchcancel', onTouchEnd);
                gameReady = true;
            }
            
            showMessage('✅ Puzzle ready! Drag the pieces into place.');
            draw();
        }
        
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            ctx.shadowColor = '#22d3ee';
            ctx.shadowBlur = 20;
            ctx.strokeStyle = '#22d3ee';
            ctx.lineWidth = 8;
            ctx.strokeRect(puzzleX - 12, puzzleY - 12, puzzleWidth + 24, puzzleHeight + 24);
            ctx.shadowBlur = 0;
            
            if (showHelpOverlay) {
                ctx.globalAlpha = 0.18;
                ctx.drawImage(sourceImg, puzzleX, puzzleY, puzzleWidth, puzzleHeight);
                ctx.globalAlpha = 1.0;
            }
            
            for (let i = 0; i < pieces.length; i++) {
                const p = pieces[i];
                ctx.drawImage(
                    sourceImg,
                    p.col * (sourceImg.width / cols),
                    p.row * (sourceImg.height / rows),
                    sourceImg.width / cols,
                    sourceImg.height / rows,
                    p.currX,
                    p.currY,
                    p.width,
                    p.height
                );
                
                ctx.strokeStyle = (p === draggedPiece) ? '#a78bfa' : '#e2e8f0';
                ctx.lineWidth = (p === draggedPiece) ? 4 : 2.5;
                ctx.shadowBlur = (p === draggedPiece) ? 12 : 4;
                ctx.shadowColor = '#a78bfa';
                ctx.strokeRect(p.currX, p.currY, p.width, p.height);
                ctx.shadowBlur = 0;
            }
            
            ctx.strokeStyle = 'rgba(255,255,255,0.15)';
            ctx.lineWidth = 1;
            for (let i = 1; i < cols; i++) {
                ctx.beginPath();
                ctx.moveTo(puzzleX + i * pieceW, puzzleY);
                ctx.lineTo(puzzleX + i * pieceW, puzzleY + puzzleHeight);
                ctx.stroke();
            }
            for (let i = 1; i < rows; i++) {
                ctx.beginPath();
                ctx.moveTo(puzzleX, puzzleY + i * pieceH);
                ctx.lineTo(puzzleX + puzzleWidth, puzzleY + i * pieceH);
                ctx.stroke();
            }
        }
        
        function getMousePos(e) {
            const rect = canvas.getBoundingClientRect();
            return {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        }
        
        function getTouchPos(e) {
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0] || e.changedTouches[0];
            return {
                x: touch.clientX - rect.left,
                y: touch.clientY - rect.top
            };
        }
        
        function onTouchStart(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            onMouseDown(mouseEvent);
        }
        
        function onTouchMove(e) {
            e.preventDefault();
            if (!draggedPiece) return;
            const touch = e.touches[0];
            const pos = {
                x: touch.clientX - canvas.getBoundingClientRect().left,
                y: touch.clientY - canvas.getBoundingClientRect().top
            };
            draggedPiece.currX = pos.x - offsetX;
            draggedPiece.currY = pos.y - offsetY;
            draw();
        }
        
        function onTouchEnd(e) {
            e.preventDefault();
            onMouseUp();
        }
        
        function onMouseDown(e) {
            const pos = getMousePos(e);
            for (let i = pieces.length - 1; i >= 0; i--) {
                const p = pieces[i];
                if (pos.x > p.currX && pos.x < p.currX + p.width &&
                    pos.y > p.currY && pos.y < p.currY + p.height) {
                    
                    draggedPiece = p;
                    offsetX = pos.x - p.currX;
                    offsetY = pos.y - p.currY;
                    
                    pieces.splice(i, 1);
                    pieces.push(p);
                    draw();
                    return;
                }
            }
        }
        
        function onMouseMove(e) {
            if (!draggedPiece) return;
            const pos = getMousePos(e);
            draggedPiece.currX = pos.x - offsetX;
            draggedPiece.currY = pos.y - offsetY;
            draw();
        }
        
        function onMouseUp() {
            if (!draggedPiece) return;
            
            const SNAP_THRESHOLD = 28;
            if (Math.abs(draggedPiece.currX - draggedPiece.correctX) < SNAP_THRESHOLD &&
                Math.abs(draggedPiece.currY - draggedPiece.correctY) < SNAP_THRESHOLD) {
                
                draggedPiece.currX = draggedPiece.correctX;
                draggedPiece.currY = draggedPiece.correctY;
            }
            
            draggedPiece = null;
            draw();
            checkWinCondition();
        }
        
        function checkWinCondition() {
            const solved = pieces.every(piece => 
                Math.abs(piece.currX - piece.correctX) < 6 && 
                Math.abs(piece.currY - piece.correctY) < 6
            );
            
            if (solved) {
                showMessage('🎉 Congratulations! You solved the puzzle!', false, true);
                createSimpleConfetti();
            }
        }
        
        function shufflePieces(redraw = true) {
            if (pieces.length === 0) return;
            
            const scatterAreaX = puzzleX + puzzleWidth + 40;
            const scatterAreaW = canvas.width - scatterAreaX - 40;
            const scatterAreaH = canvas.height - 120;
            
            pieces.forEach(piece => {
                piece.currX = scatterAreaX + Math.random() * scatterAreaW;
                piece.currY = 60 + Math.random() * scatterAreaH;
            });
            
            if (redraw) draw();
        }
        
        function resetPuzzle() {
            if (pieces.length === 0) return;
            shufflePieces(true);
            showMessage('Pieces reset and shuffled!');
        }
        
        function toggleHelp() {
            const modal = document.getElementById('help-modal');
            if (modal.style.display === 'flex') {
                modal.style.display = 'none';
                showHelpOverlay = false;
            } else {
                document.getElementById('original-image').src = sourceImg.src;
                modal.style.display = 'flex';
                showHelpOverlay = true;
            }
            if (gameReady) draw();
        }
        
        function showMessage(text, isError = false, isWin = false) {
            const msgEl = document.getElementById('message');
            msgEl.style.color = isError ? '#f87171' : (isWin ? '#67e8f9' : '#e2e8f0');
            msgEl.innerHTML = text;
            
            if (isWin) {
                setTimeout(() => {
                    if (msgEl.innerHTML === text) msgEl.innerHTML = '';
                }, 8000);
            }
        }
        
        function createSimpleConfetti() {
            let count = 80;
            const colors = ['#22d3ee', '#a78bfa', '#67e8f9', '#f472b6'];
            while (count--) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height * 0.4;
                ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
                ctx.fillRect(x, y, 8, 8);
                setTimeout(() => {
                    if (ctx) ctx.clearRect(x, y, 8, 8);
                }, 1200 + Math.random() * 800);
            }
        }
        
        window.onload = () => {
            // Auto-load a nice demo puzzle when the page opens
            setTimeout(() => {
                if (!gameReady) createPuzzle();
            }, 500);
        };
    </script>
</body>
</html>
"""

# Write HTML to a temporary file so it works cleanly
def create_and_open_puzzle():
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_file_path = f.name
    
    print("✅ Puzzle game generated successfully!")
    print(f"📄 Temporary file created: {temp_file_path}")
    print("\n🌐 Opening in your default web browser now...\n")
    
    # Open in browser
    webbrowser.open(f'file://{os.path.abspath(temp_file_path)}')
    
    # Optional: clean up file when script exits
    @atexit.register
    def cleanup():
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == "__main__":
    create_and_open_puzzle()
    print("Game is running in your browser! 🎉")
    print("You can close this terminal window anytime.")
    input("\nPress Enter to exit this launcher...")