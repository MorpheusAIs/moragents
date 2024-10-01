import React, { useState, useEffect } from "react";
import { FaCog } from "react-icons/fa";
import classes from "./index.module.css";

interface Credentials {
  apiKey: string;
  apiSecret: string;
  accessToken: string;
  accessTokenSecret: string;
  bearerToken: string;
  cdpApiKey: string;
  cdpApiSecret: string;
}

const SettingsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [credentials, setCredentials] = useState<Credentials>({
    apiKey: "",
    apiSecret: "",
    accessToken: "",
    accessTokenSecret: "",
    bearerToken: "",
    cdpApiKey: "",
    cdpApiSecret: "",
  });
  const [displayCredentials, setDisplayCredentials] = useState<Credentials>({
    apiKey: "",
    apiSecret: "",
    accessToken: "",
    accessTokenSecret: "",
    bearerToken: "",
    cdpApiKey: "",
    cdpApiSecret: "",
  });

  useEffect(() => {
    const storedCredentials: Credentials = {
      apiKey: localStorage.getItem("apiKey") || "",
      apiSecret: localStorage.getItem("apiSecret") || "",
      accessToken: localStorage.getItem("accessToken") || "",
      accessTokenSecret: localStorage.getItem("accessTokenSecret") || "",
      bearerToken: localStorage.getItem("bearerToken") || "",
      cdpApiKey: localStorage.getItem("cdpApiKey") || "",
      cdpApiSecret: localStorage.getItem("cdpApiSecret") || "",
    };
    setCredentials(storedCredentials);
    setDisplayCredentials(Object.fromEntries(
      Object.entries(storedCredentials).map(([key, value]) => [key, obscureCredential(value)])
    ) as Credentials);
  }, []);

  const obscureCredential = (credential: string) => {
    if (credential.length <= 5) return credential;
    return "***" + credential.slice(-5);
  };

  const handleSaveCredentials = () => {
    Object.entries(credentials).forEach(([key, value]) => {
      localStorage.setItem(key, value);
    });
    setDisplayCredentials(Object.fromEntries(
      Object.entries(credentials).map(([key, value]) => [key, obscureCredential(value)])
    ) as Credentials);
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials((prev) => ({ ...prev, [name]: value }));
  };

  const getFieldSet = (group: string): (keyof Credentials)[] => {
    switch (group) {
      case "x":
        return ["apiKey", "apiSecret", "accessToken", "accessTokenSecret", "bearerToken"];
      case "cdp":
        return ["cdpApiKey", "cdpApiSecret"];
      default:
        return [];
    }
  };

  const getFieldLabel = (key: keyof Credentials): string => {
    const labels: Record<keyof Credentials, string> = {
      apiKey: "API Key",
      apiSecret: "API Secret",
      accessToken: "Access Token",
      accessTokenSecret: "Access Token Secret",
      bearerToken: "Bearer Token",
      cdpApiKey: "CDP API Key",
      cdpApiSecret: "CDP API Secret",
    };
    return labels[key] || key;
  };

  const renderCredentialFields = (group: string) => {
    const fields = getFieldSet(group);
    return fields.map((key) => (
      <div key={key} className={classes.credentialField}>
        <p className={classes.apiKeyDisplay}>
          Current {getFieldLabel(key)}:{" "}
          <span className={classes.apiKeyValue}>
            {displayCredentials[key] || "Not set"}
          </span>
        </p>
        <input
          className={classes.apiKeyInput}
          type="password"
          name={key}
          placeholder={`Enter new ${getFieldLabel(key)}`}
          value={credentials[key]}
          onChange={handleInputChange}
        />
      </div>
    ));
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
            <button
              className={classes.closeButton}
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>

            <h2 className={classes.modalHeader}>X API Settings</h2>
            <p className={classes.modalDescription}>
              All of these credentials are necessary. The API Key and API Secret
              are the API keys found in the developer portal. The Access Token
              and Access Token Secret will be generated for your particular
              user. The Bearer Token is used for authentication. Both the Access
              Token Secret and Bearer Token are found in the X Developer Portal
              under the Authentication Tokens section.
            </p>
            <div className={classes.credentialsSection}>
              {renderCredentialFields("x")}
            </div>

            <h2 className={classes.modalHeader}>Coinbase Developer Platform Settings</h2>
            <p className={classes.modalDescription}>
              Enter your Coinbase Developer Platform API credentials here. You can find these in your Coinbase Developer account settings.
            </p>
            <div className={classes.credentialsSection}>
              {renderCredentialFields("cdp")}
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