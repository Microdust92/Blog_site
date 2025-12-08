// Digital Rain Effect
const canvas = document.createElement('canvas');
canvas.id = 'matrix-rain';
canvas.style.position = 'fixed';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100vw';
canvas.style.height = '100vh';
canvas.style.zIndex = '-1';
canvas.style.opacity = '0.15';
canvas.style.pointerEvents = 'none';
document.body.insertBefore(canvas, document.body.firstChild);

const ctx = canvas.getContext('2d');

// Set canvas size
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Recalculate columns
    const columns = Math.floor(canvas.width / fontSize);
    drops.length = columns;
    for (let i = 0; i < columns; i++) {
        if (drops[i] === undefined) {
            drops[i] = Math.floor(Math.random() * canvas.height / fontSize);
        }
    }
}

// Matrix characters
const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
//const chars = '01';
const fontSize = 14;
let drops = [];

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Draw function
function draw() {
    // Fade effect
    ctx.fillStyle = 'rgba(15, 20, 25, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw characters
    ctx.fillStyle = '#28b4f0'; // Cyan color
    ctx.font = fontSize + 'px monospace';
    
    for (let i = 0; i < drops.length; i++) {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        
        // Reset drop
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.95) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}

// Animation loop
setInterval(draw, 50);