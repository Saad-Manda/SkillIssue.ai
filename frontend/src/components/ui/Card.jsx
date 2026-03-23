export const Card = ({ children, title, subtitle, style }) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--bg-primary)',
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-md)',
        padding: '32px',
        width: '100%',
        maxWidth: '440px',
        margin: '0 auto',
        ...style
      }}
    >
      {(title || subtitle) && (
        <div style={{ marginBottom: '24px', textAlign: 'center' }}>
          {title && <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>{title}</h2>}
          {subtitle && <p style={{ color: 'var(--text-secondary)', fontSize: '15px' }}>{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
};
