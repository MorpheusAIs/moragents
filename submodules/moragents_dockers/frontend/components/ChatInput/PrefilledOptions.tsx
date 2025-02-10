import React, { useState, useEffect } from "react";
import { Box } from "@chakra-ui/react";
import { prefilledOptionsMap } from "./PrefilledOptions.constants";
import styles from "./PrefilledOptions.module.css";
import API_BASE_URL from "../../config";

const PrefilledOptions = ({
  onSelect,
  isWidgetOpen = false,
  isSidebarOpen = true,
}: {
  onSelect: (text: string) => void;
  isWidgetOpen?: boolean;
  isSidebarOpen?: boolean;
}) => {
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/agents/available`);
        const data = await response.json();
        setSelectedAgents(data.selected_agents);
      } catch (error) {
        console.error("Failed to fetch agents:", error);
      }
    };
    fetchAgents();
  }, []);

  const toggleSection = (agentName: string, rowIndex: number) => {
    if (!isMobile) return;
    setExpandedSection(expandedSection === agentName ? null : agentName);
  };

  // Group agents into pairs for mobile layout
  const agentRows = selectedAgents.reduce((result, agent, index) => {
    const rowIndex = Math.floor(index / 2);
    if (!result[rowIndex]) {
      result[rowIndex] = [];
    }
    result[rowIndex].push(agent);
    return result;
  }, [] as string[][]);

  return (
    <div className={styles.prefilledContainer}>
      <div className={styles.prefilledInner}>
        {isMobile
          ? agentRows.map((row, rowIndex) => (
              <div key={rowIndex} className={styles.rowWrapper}>
                {/* Title row */}
                <div className={styles.titleRow}>
                  {row.map((agentName, columnIndex) => {
                    const option = prefilledOptionsMap[agentName];
                    if (!option) return null;

                    const isExpanded = expandedSection === agentName;
                    return (
                      <div
                        key={agentName}
                        className={`${styles.prefilledSection} ${
                          isExpanded ? styles.expanded : ""
                        }`}
                      >
                        <button
                          className={styles.sectionTitle}
                          onClick={() => toggleSection(agentName, rowIndex)}
                        >
                          <Box className={styles.sectionIcon}>
                            {option.icon}
                          </Box>
                          {option.title}
                        </button>
                      </div>
                    );
                  })}
                </div>

                {/* Examples row - only shown when expanded */}
                {row.map((agentName, columnIndex) => {
                  const option = prefilledOptionsMap[agentName];
                  if (!option || expandedSection !== agentName) return null;

                  return (
                    <div
                      key={`${agentName}-examples`}
                      className={`${styles.expandedExamples} ${
                        columnIndex === 0
                          ? styles.firstColumn
                          : styles.secondColumn
                      }`}
                    >
                      {option.examples.map((example, exampleIndex) => (
                        <button
                          key={exampleIndex}
                          className={styles.exampleButton}
                          onClick={() => onSelect(example.text)}
                        >
                          {example.text}
                        </button>
                      ))}
                    </div>
                  );
                })}
              </div>
            ))
          : // Desktop layout (always expanded)
            selectedAgents.map((agentName) => {
              const option = prefilledOptionsMap[agentName];
              if (!option) return null;

              return (
                <div key={agentName} className={styles.prefilledSection}>
                  <div className={styles.sectionTitle}>
                    <Box className={styles.sectionIcon}>{option.icon}</Box>
                    {option.title}
                  </div>
                  <div className={styles.examplesList}>
                    {option.examples.map((example, exampleIndex) => (
                      <button
                        key={exampleIndex}
                        className={styles.exampleButton}
                        onClick={() => onSelect(example.text)}
                      >
                        {example.text}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
      </div>
    </div>
  );
};

export default PrefilledOptions;
