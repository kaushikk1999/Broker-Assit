"use client";
// Opens the assistant and asks a question (via a window event the Assistant listens for).
export default function AskButton({ query, children, className = "btn" }) {
  return (
    <button className={className} type="button"
      onClick={() => window.dispatchEvent(new CustomEvent("ba-ask", { detail: query }))}>
      {children}
    </button>
  );
}
