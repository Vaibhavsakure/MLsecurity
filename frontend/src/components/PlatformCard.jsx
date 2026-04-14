export default function PlatformCard({ platform, config, onClick }) {
  return (
    <div
      className="platform-card"
      style={{ "--platform-color": config.color }}
      onClick={() => onClick(platform)}
      id={`platform-${platform}`}
    >
      {config.synthetic && (
        <span className="synthetic-badge">⚗️ Synthetic Data</span>
      )}
      <div
        className="platform-icon"
        dangerouslySetInnerHTML={{ __html: config.icon }}
      />
      <h3>{config.name}</h3>
      <p>{config.description}</p>
    </div>
  );
}
