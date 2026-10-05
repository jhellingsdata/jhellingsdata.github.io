// Vega draws charts to canvas once and does not redraw when a web font arrives later,
// so wait for Circular Std (declared in css/circular-std.css) before calling vegaEmbed.
// Resolves even if the font fails, so charts still render with the fallback.
function circularReady() {
    return Promise.all(
        ['400', '500', '700'].map(weight => document.fonts.load(`${weight} 1em "Circular Std"`))
    ).catch(() => {});
}
