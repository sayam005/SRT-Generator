/**
 * PositionControls.jsx — Subtitle position and font size controls.
 */

/**
 * @param {{
 *   position: string,
 *   fontSize: number,
 *   onPositionChange: (position: string) => void,
 *   onFontSizeChange: (size: number) => void,
 *   disabled: boolean
 * }} props
 */
export default function PositionControls({
    position = "bottom",
    fontSize = 24,
    onPositionChange,
    onFontSizeChange,
    disabled = false,
}) {
    return (
        <div id="position-controls" className="position-controls">
            <div className="control-group">
                <label className="control-label">Subtitle Position</label>
                <div className="radio-group">
                    {["top", "bottom"].map((pos) => (
                        <label key={pos} className="radio-option">
                            <input
                                type="radio"
                                name="position"
                                value={pos}
                                checked={position === pos}
                                onChange={() => onPositionChange(pos)}
                                disabled={disabled}
                            />
                            <span>{pos.charAt(0).toUpperCase() + pos.slice(1)}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="control-group">
                <label className="control-label">
                    Font Size: <strong>{fontSize}px</strong>
                </label>
                <input
                    type="range"
                    min={16}
                    max={48}
                    value={fontSize}
                    onChange={(e) => onFontSizeChange(Number(e.target.value))}
                    disabled={disabled}
                    className="font-slider"
                />
            </div>
        </div>
    );
}
