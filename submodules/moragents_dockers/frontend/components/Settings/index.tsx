import React, { useState, useEffect } from "react";
import { FaCog } from "react-icons/fa";
import classes from "./index.module.css";

const SettingsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [credentials, setCredentials] = useState({
    apiKey: "",
    apiSecret: "",
    accessToken: "",
    accessTokenSecret: "",
    bearerToken: "",
  });
  const [displayCredentials, setDisplayCredentials] = useState({
    apiKey: "",
    apiSecret: "",
    accessToken: "",
    accessTokenSecret: "",
    bearerToken: "",
  });

  useEffect(() => {
    const storedCredentials = {
      apiKey: localStorage.getItem("apiKey") || "",
      apiSecret: localStorage.getItem("apiSecret") || "",
      accessToken: localStorage.getItem("accessToken") || "",
      accessTokenSecret: localStorage.getItem("accessTokenSecret") || "",
      bearerToken: localStorage.getItem("bearerToken") || "",
      cdpApiKey: localStorage.getItem("cdpApiKey") || "",
      cdpApiSecret: localStorage.getItem("cdpApiSecret") || "",
    };
    setCredentials(storedCredentials);
    setDisplayCredentials({
      apiKey: obscureCredential(storedCredentials.apiKey),
      apiSecret: obscureCredential(storedCredentials.apiSecret),
      accessToken: obscureCredential(storedCredentials.accessToken),
      accessTokenSecret: obscureCredential(storedCredentials.accessTokenSecret),
      bearerToken: obscureCredential(storedCredentials.bearerToken),
      cdpApiKey: obscureCredential(storedCredentials.cdpApiKey),
      cdpApiSecret: obscureCredential(storedCredentials.cdpApiSecret),
    });
  }, []);

  const obscureCredential = (credential: string) => {
    if (credential.length <= 5) return credential;
    return "***" + credential.slice(-5);
  };

  const handleSaveCredentials = () => {
    Object.entries(credentials).forEach(([key, value]) => {
      localStorage.setItem(key, value);
    });
    setDisplayCredentials({
      apiKey: obscureCredential(credentials.apiKey),
      apiSecret: obscureCredential(credentials.apiSecret),
      accessToken: obscureCredential(credentials.accessToken),
      accessTokenSecret: obscureCredential(credentials.accessTokenSecret),
      bearerToken: obscureCredential(credentials.bearerToken),
      cdpApiKey: obscureCredential(credentials.cdpApiKey),
      cdpApiSecret: obscureCredential(credentials.cdpApiSecret),
    });
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials((prev) => ({ ...prev, [name]: value }));
  };

  const getFieldLabel = (key: string) => {
    switch (key) {
      case "apiKey":
        return "API Key";
      case "apiSecret":
        return "API Secret";
      case "accessToken":
        return "Access Token";
      case "accessTokenSecret":
        return "Access Token Secret";
      case "bearerToken":
        return "Bearer Token";
      case "cdpApiKey":
        return "CDP API Key";
      case "cdpApiSecret":
        return "CDP API Secret";
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
              All of these credentials are necessary. The API Key and API Secret
              are the API keys found in the developer portal. The Access Token
              and Access Token Secret will be generated for your particular
              user. The Bearer Token is used for authentication. Both the Access
              Token Secret and Bearer Token are found in the X Developer Portal
              under the Authentication Tokens section.
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
                    type={value ? "text" : "password"}
                    name={key}
                    placeholder={`Enter new ${getFieldLabel(key)}`}
                    value={
                      value
                        ? value.replace(/./g, (char, index) =>
                            index < value.length - 4 ? "•" : char
                          )
                        : ""
                    }
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
