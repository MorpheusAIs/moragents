import React, { useState, useEffect } from "react";
import { FaCog } from "react-icons/fa";
import classes from "./index.module.css";

const SettingsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [credentials, setCredentials] = useState({
    consumerKey: "",
    consumerSecret: "",
    accessToken: "",
    accessTokenSecret: "",
  });
  const [displayCredentials, setDisplayCredentials] = useState({
    consumerKey: "",
    consumerSecret: "",
    accessToken: "",
    accessTokenSecret: "",
  });

  useEffect(() => {
    const storedCredentials = {
      consumerKey: localStorage.getItem("consumerKey") || "",
      consumerSecret: localStorage.getItem("consumerSecret") || "",
      accessToken: localStorage.getItem("accessToken") || "",
      accessTokenSecret: localStorage.getItem("accessTokenSecret") || "",
    };
    setCredentials(storedCredentials);
    setDisplayCredentials({
      consumerKey: obscureCredential(storedCredentials.consumerKey),
      consumerSecret: obscureCredential(storedCredentials.consumerSecret),
      accessToken: obscureCredential(storedCredentials.accessToken),
      accessTokenSecret: obscureCredential(storedCredentials.accessTokenSecret),
    });
  }, []);

  const obscureCredential = (credential: string) => {
    if (credential.length <= 5) return credential;
    return "*".repeat(credential.length - 5) + credential.slice(-5);
  };

  const handleSaveCredentials = () => {
    Object.entries(credentials).forEach(([key, value]) => {
      localStorage.setItem(key, value);
    });
    setDisplayCredentials({
      consumerKey: obscureCredential(credentials.consumerKey),
      consumerSecret: obscureCredential(credentials.consumerSecret),
      accessToken: obscureCredential(credentials.accessToken),
      accessTokenSecret: obscureCredential(credentials.accessTokenSecret),
    });
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials((prev) => ({ ...prev, [name]: value }));
  };

  const getFieldLabel = (key: string) => {
    switch (key) {
      case "consumerKey":
        return "Consumer Key";
      case "consumerSecret":
        return "Consumer Secret";
      case "accessToken":
        return "Access Token";
      case "accessTokenSecret":
        return "Access Token Secret";
      default:
        return key;
    }
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
            <h2 className={classes.modalHeader}>X API Settings</h2>
            <p className={classes.modalDescription}>
              All of these credentials are necessary. The Consumer Key and
              Consumer Secret are the API keys found in the developer portal.
              The Access Token and Access Token Secret are the OAuth 2 Client ID
              and Client Secret.
            </p>
            <br />
            <button
              className={classes.closeButton}
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
            <div>
              {Object.entries(credentials).map(([key, value]) => (
                <div key={key} className={classes.credentialField}>
                  <p className={classes.apiKeyDisplay}>
                    Current {getFieldLabel(key)}:{" "}
                    <span className={classes.apiKeyValue}>
                      {displayCredentials[
                        key as keyof typeof displayCredentials
                      ] || "Not set"}
                    </span>
                  </p>
                  <input
                    className={classes.apiKeyInput}
                    type="password"
                    name={key}
                    placeholder={`Enter new ${getFieldLabel(key)}`}
                    value={value}
                    onChange={handleInputChange}
                  />
                </div>
              ))}
            </div>
            <div className={classes.modalFooter}>
              <button
                className={classes.saveButton}
                onClick={handleSaveCredentials}
              >
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
