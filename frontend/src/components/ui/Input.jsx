export const Input = ({ label, id, error, multiline, rows = 4, ...props }) => {
  const Component = multiline ? 'textarea' : 'input';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px' }}>
      {label && (
        <label htmlFor={id} style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>
          {label}
        </label>
      )}
      <Component
        id={id}
        rows={multiline ? rows : undefined}
        style={{
          padding: '10px 14px',
          border: `1px solid ${error ? '#EF4444' : 'var(--border-color)'}`,
          borderRadius: '6px',
          fontSize: '16px',
          fontFamily: 'inherit',
          outline: 'none',
          transition: 'border-color 0.2s, box-shadow 0.2s',
          backgroundColor: 'var(--bg-primary)',
          color: 'var(--text-primary)',
          resize: multiline ? 'vertical' : undefined
        }}
        onFocus={(e) => {
          e.target.style.borderColor = 'var(--text-primary)';
          e.target.style.boxShadow = '0 0 0 2px var(--focus-ring, rgba(255,255,255,0.2))';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = error ? '#EF4444' : 'var(--border-color)';
          e.target.style.boxShadow = 'none';
        }}
        {...props}
      />
      {error && <span style={{ fontSize: '13px', color: '#EF4444' }}>{error}</span>}
    </div>
  );
};
