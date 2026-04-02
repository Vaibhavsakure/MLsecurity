export default function PlatformCard({ platform, config, onClick }) {
  return (
    <div
      className="platform-card"
      style={{ "--platform-color": config.color }}
      onClick={() => onClick(platform)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick(platform)}
      id={`platform-card-${platform}`}
    >
      <div className="platform-icon" dangerouslySetInnerHTML={{ __html: config.icon }} />
      <h3>{config.name}</h3>
      <p>{config.description}</p>
    </div>
  );
}
