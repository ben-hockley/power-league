// Badge option toggle
document.getElementById('badge_url_option').addEventListener('change', function() {
    document.getElementById('badge_url_fields').style.display = this.checked ? 'block' : 'none';
    document.getElementById('badge_default_fields').style.display = this.checked ? 'none' : 'block';
});
document.getElementById('badge_default_option').addEventListener('change', function() {
    document.getElementById('badge_url_fields').style.display = this.checked ? 'none' : 'block';
    document.getElementById('badge_default_fields').style.display = this.checked ? 'block' : 'none';
});

// Show/hide logo preview only if custom badge URL is selected
function updateLogoPreviewVisibility() {
    const urlOption = document.getElementById('badge_url_option').checked;
    const logoInput = document.getElementById('team_logo');
    const logoPreview = document.getElementById('logo_preview');
    if (urlOption && logoInput.value) {
    logoPreview.src = logoInput.value;
    logoPreview.style.display = 'block';
    } else {
    logoPreview.style.display = 'none';
    }
}

// Logo URL preview
document.getElementById('team_logo').addEventListener('input', updateLogoPreviewVisibility);
document.getElementById('badge_url_option').addEventListener('change', updateLogoPreviewVisibility);
document.getElementById('badge_default_option').addEventListener('change', updateLogoPreviewVisibility);

// Badge SVG preview
document.getElementById('preview_badge_btn').addEventListener('click', function() {
    const shape = document.getElementById('badge_shape').value;
    const icon = document.getElementById('badge_icon').value;
    const primary = document.getElementById('team_primary_color').value;
    const secondary = document.getElementById('team_secondary_color').value;
    const name = document.getElementById('team_name').value || "TEAM";
    let svg = '';
    // Larger SVG badge generator with smaller text
    if (shape === 'shield') {
    svg = `<svg width="220" height="320" viewBox="0 0 220 320">
        <path d="M20 40 Q110 0 200 40 L200 160 Q110 280 20 160 Z" fill="${primary}" stroke="${secondary}" stroke-width="8"/>
        <text x="110" y="120" text-anchor="middle" font-size="48" fill="${secondary}" dominant-baseline="middle">${icon}</text>
        <text x="110" y="200" text-anchor="middle" font-size="22" fill="${secondary}" font-weight="bold" dominant-baseline="middle">${name.substring(0,16)}</text>
    </svg>`;
    } else if (shape === 'circle') {
    svg = `<svg width="220" height="220" viewBox="0 0 220 220">
        <circle cx="110" cy="110" r="100" fill="${primary}" stroke="${secondary}" stroke-width="8"/>
        <text x="110" y="110" text-anchor="middle" font-size="48" fill="${secondary}" dominant-baseline="middle">${icon}</text>
        <text x="110" y="170" text-anchor="middle" font-size="22" fill="${secondary}" font-weight="bold" dominant-baseline="middle">${name.substring(0,16)}</text>
    </svg>`;
    } else if (shape === 'square') {
    svg = `<svg width="220" height="220" viewBox="0 0 220 220">
        <rect x="20" y="20" width="180" height="180" rx="30" fill="${primary}" stroke="${secondary}" stroke-width="8"/>
        <text x="110" y="110" text-anchor="middle" font-size="48" fill="${secondary}" dominant-baseline="middle">${icon}</text>
        <text x="110" y="185" text-anchor="middle" font-size="22" fill="${secondary}" font-weight="bold" dominant-baseline="middle">${name.substring(0,16)}</text>
    </svg>`;
    } else if (shape === 'hex') {
    svg = `<svg width="220" height="220" viewBox="0 0 220 220">
        <polygon points="110,20 200,60 200,160 110,200 20,160 20,60" fill="${primary}" stroke="${secondary}" stroke-width="8"/>
        <text x="110" y="110" text-anchor="middle" font-size="48" fill="${secondary}" dominant-baseline="middle">${icon}</text>
        <text x="110" y="185" text-anchor="middle" font-size="22" fill="${secondary}" font-weight="bold" dominant-baseline="middle">${name.substring(0,16)}</text>
    </svg>`;
    }
    document.getElementById('badge_svg_preview').innerHTML = svg;
    document.getElementById('badge_svg_data').value = svg;
});

// Color preview SVGs
function updateColorPreviews() {
    const primary = document.getElementById('team_primary_color').value;
    const secondary = document.getElementById('team_secondary_color').value;
    // Simple circle shape for preview
    const svg1 = `<svg width="80" height="80"><circle cx="40" cy="40" r="35" fill="${primary}" stroke="#ccc" stroke-width="2"/><text x="40" y="48" text-anchor="middle" font-size="20" fill="${secondary}" font-weight="bold">Aa</text></svg>`;
    const svg2 = `<svg width="80" height="80"><circle cx="40" cy="40" r="35" fill="${secondary}" stroke="#ccc" stroke-width="2"/><text x="40" y="48" text-anchor="middle" font-size="20" fill="${primary}" font-weight="bold">Aa</text></svg>`;
    document.getElementById('color_preview_1').innerHTML = svg1;
    document.getElementById('color_preview_2').innerHTML = svg2;
}

document.getElementById('team_primary_color').addEventListener('input', updateColorPreviews);
document.getElementById('team_secondary_color').addEventListener('input', updateColorPreviews);

// Initialize previews on page load
window.addEventListener('DOMContentLoaded', function() {
    updateColorPreviews();
    updateLogoPreviewVisibility();
});