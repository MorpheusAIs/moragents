import React, { useState, useEffect } from "react";
import { FaCog } from "react-icons/fa";
import classes from "./index.module.css";

const SettingsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [xApiKey, setXApiKey] = useState("");
  const [displayApiKey, setDisplayApiKey] = useState("");

  useEffect(() => {
    const storedApiKey = localStorage.getItem("xApiKey") || "";
    setXApiKey(storedApiKey);
    setDisplayApiKey(obscureApiKey(storedApiKey));
  }, []);

  const obscureApiKey = (key: string) => {
    if (key.length <= 5) return key;
    return "*".repeat(key.length - 5) + key.slice(-5);
  };

  const handleSaveApiKey = () => {
    localStorage.setItem("xApiKey", xApiKey);
    setDisplayApiKey(obscureApiKey(xApiKey));
    setIsOpen(false);
  };

  return (
    <>
      <button
        className={classes.settingsButton}
        onClick={() => setIsOpen(true)}
      >
        <FaCog className={classes.settingsIcon} />
        Settings
      </button>

      {isOpen && (
        <div className={classes.modalOverlay} onClick={() => setIsOpen(false)}>
          <div
            className={classes.modalContent}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className={classes.modalHeader}>Settings</h2>
            <button
              className={classes.closeButton}
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
            <div>
              <p className={classes.apiKeyDisplay}>
                Current X API Key: {displayApiKey || "No API key set"}
              </p>
              <input
                className={classes.apiKeyInput}
                type="password"
                placeholder="Enter new X API Key"
                value={xApiKey}
                onChange={(e) => setXApiKey(e.target.value)}
              />
            </div>
            <div className={classes.modalFooter}>
              <button className={classes.saveButton} onClick={handleSaveApiKey}>
                Save
              </button>
              <button
                className={classes.cancelButton}
                onClick={() => setIsOpen(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SettingsButton;
