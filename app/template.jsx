// Re-mounts on every route change → plays the entrance animation for smooth page transitions.
export default function Template({ children }) {
  return <div className="page-enter">{children}</div>;
}
