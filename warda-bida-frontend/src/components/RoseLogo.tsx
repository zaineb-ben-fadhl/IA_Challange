export function RoseLogo() {
  // Logo SVG minimaliste “rose blanche” (à remplacer par votre vrai logo si vous l’avez)
  return (
    <svg width="46" height="46" viewBox="0 0 64 64" fill="none" aria-label="Warda Bida Logo">
      <defs>
        <linearGradient id="petal" x1="12" y1="10" x2="52" y2="56" gradientUnits="userSpaceOnUse">
          <stop stopColor="#ffffff" stopOpacity="0.95" />
          <stop offset="1" stopColor="#ffe6ef" stopOpacity="0.95" />
        </linearGradient>
        <linearGradient id="stroke" x1="10" y1="8" x2="54" y2="56" gradientUnits="userSpaceOnUse">
          <stop stopColor="#f2c6d5" />
          <stop offset="1" stopColor="#d9a7b8" />
        </linearGradient>
      </defs>

      <circle cx="32" cy="32" r="30" fill="rgba(255,255,255,0.10)" stroke="url(#stroke)" strokeWidth="1.2" />
      <path
        d="M32 14c6 6 10 10 10 16s-4 12-10 16c-6-4-10-10-10-16s4-10 10-16Z"
        fill="url(#petal)"
        stroke="url(#stroke)"
        strokeWidth="1.2"
      />
      <path
        d="M18 26c8 0 14 6 14 14-8 0-14-6-14-14Z"
        fill="url(#petal)"
        stroke="url(#stroke)"
        strokeWidth="1.2"
        opacity="0.92"
      />
      <path
        d="M46 26c-8 0-14 6-14 14 8 0 14-6 14-14Z"
        fill="url(#petal)"
        stroke="url(#stroke)"
        strokeWidth="1.2"
        opacity="0.92"
      />
      <circle cx="32" cy="36" r="4.5" fill="#fff" stroke="url(#stroke)" strokeWidth="1.2" />
    </svg>
  );
}