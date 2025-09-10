import React, { forwardRef, useImperativeHandle, useState } from "react";
import axios from "axios";

const openaiApiKey = process.env.OPEN_AI_API_KEY;
export type OpenAIAssistantHandle = {
  sendMessage: (message: string) => Promise<string>;
};

const OpenAIAssistant = forwardRef<OpenAIAssistantHandle>((_, ref) => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    [
      {
        role: "system",
        content: `You are a professional job interviewer. Your role is to evaluate the candidate's responses by asking thoughtful, insightful, and probing follow-up questions. 
Your responsibilities include:
  - Assessing the candidate's skills, experience, and fit for the role.
  - Asking clarifying questions to understand the candidate's perspective.
  - Encouraging the candidate to elaborate on their experiences with specific examples.
  - Being friendly, respectful, and maintaining a professional tone at all times.
  - Adjusting your questions based on the candidate's previous answers.
When a candidate responds, ask a relevant follow-up question that both challenges and supports them, prompting deeper discussion. Always keep your questions concise yet open-ended, and ensure your tone remains professional and encouraging.`,
      },
    ]
  );

  useImperativeHandle(ref, () => ({
    async sendMessage(message: string) {
      const newMessages = [...messages, { role: "user", content: message }];
      setMessages(newMessages);

      try {
        const response = await axios.post(
          "https://api.openai.com/v1/chat/completions",
          {
            model: "gpt-4",
            messages: newMessages,
          },
          {
            headers: {
              Authorization: `Bearer ${openaiApiKey}`,
              "Content-Type": "application/json",
            },
          }
        );

        const botMessage = response.data.choices[0].message.content;
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: botMessage },
        ]);

        return botMessage;
      } catch (error) {
        console.error("Error fetching OpenAI response:", error);
        return "Sorry, something went wrong.";
      }
    },
  }));

  return null; // No UI needed
});

export default OpenAIAssistant;
