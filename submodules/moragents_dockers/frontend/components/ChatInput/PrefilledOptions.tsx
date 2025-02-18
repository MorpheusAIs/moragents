import React, { useState, useEffect } from "react";
import {
  prefilledOptionsMap,
  OPTION_GROUPS,
} from "./PrefilledOptions.constants";
import styles from "./PrefilledOptions.module.css";

const PrefilledOptions = ({
  onSelect,
  isSidebarOpen = true,
}: {
  onSelect: (text: string) => void;
  isSidebarOpen: boolean;
}) => {
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [isExamplesPanelVisible, setIsExamplesPanelVisible] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const handleGroupClick = (group: string) => {
    if (selectedGroup === group) {
      setIsExamplesPanelVisible(false);
      setTimeout(() => setSelectedGroup(null), 200);
    } else {
      setIsExamplesPanelVisible(false);
      setTimeout(() => {
        setSelectedGroup(group);
        setIsExamplesPanelVisible(true);
      }, 200);
    }
  };

  const containerStyle = isMobile
    ? {}
    : {
        paddingLeft: isSidebarOpen ? "43%" : "20%",
        paddingRight: "20%",
      };

  const renderExamples = () => {
    if (!selectedGroup) return null;

    return (
      <div
        className={`${styles.examplesPanel} ${
          isExamplesPanelVisible ? styles.visible : ""
        }`}
      >
        {OPTION_GROUPS[selectedGroup as keyof typeof OPTION_GROUPS].map(
          (agentType) => {
            const option = prefilledOptionsMap[agentType];
            if (!option) return null;

            return (
              <div key={agentType} className={styles.exampleGroup}>
                <div className={styles.exampleHeader}>
                  <span className={styles.exampleIcon}>{option.icon}</span>
                  <span className={styles.exampleTitle}>{option.title}</span>
                </div>
                <div className={styles.exampleButtons}>
                  {option.examples.map((example, index) => (
                    <button
                      key={index}
                      onClick={() => onSelect(example.text)}
                      className={styles.exampleButton}
                    >
                      {example.text}
                    </button>
                  ))}
                </div>
              </div>
            );
          }
        )}
      </div>
    );
  };

  return (
    <div className={styles.prefilledContainer} style={containerStyle}>
      <div className={styles.prefilledInner}>
        <div className={styles.pillsContainer}>
          {Object.keys(OPTION_GROUPS).map((group) => (
            <button
              key={group}
              onClick={() => handleGroupClick(group)}
              className={`${styles.pillButton} ${
                selectedGroup === group ? styles.selected : ""
              }`}
            >
              {group}
            </button>
          ))}
        </div>
        {renderExamples()}
      </div>
    </div>
  );
};

export default PrefilledOptions;
