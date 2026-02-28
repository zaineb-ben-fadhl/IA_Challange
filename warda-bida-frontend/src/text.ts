const TITLE_RE =
  /^(résumé général|propriétés principales|points importants|limitations|alternatives et complémentarité|réglementation|statut légal|dosages recommandés|table de conversion rapide|spécifications techniques|caractéristiques du produit|mode d'emploi en production|points de contrôle)$/i;

const ALL_CAPS_TITLE_RE = /^[A-ZÀ-ÖØ-Ý0-9 ()°/%*.-]{6,}$/;

function isTitleLine(line: string): boolean {
  const s = line.trim();
  if (!s) return false;
  if (TITLE_RE.test(s)) return true;
  // ex: "Acide Ascorbique (E300)"
  if (ALL_CAPS_TITLE_RE.test(s) && s.length <= 60) return true;
  return false;
}

function isBulletLine(line: string): boolean {
  const s = line.trim();
  return /^[-–•]\s+/.test(s);
}

function normalizeBullet(line: string): string {
  const s = line.trim().replace(/^[–•-]\s+/, "");
  return `- ${s}`;
}

export function cleanFragmentText(input: string): string {
  let s = (input ?? "").replace(/\r/g, "");

  // Remplacer puces bizarres
  s = s.replace(/[•]+/g, "-");

  // Split en lignes + trim
  const rawLines = s.split("\n").map((l) => l.replace(/\s+/g, " ").trim());

  // Enlever lignes vides
  const lines = rawLines.filter((l) => l.length > 0);

  const out: string[] = [];
  let buffer = "";

  const flushBuffer = () => {
    if (buffer.trim()) out.push(buffer.trim());
    buffer = "";
  };

  for (const line of lines) {
    if (isTitleLine(line)) {
      flushBuffer();
      out.push(line.trim());
      continue;
    }

    if (isBulletLine(line)) {
      flushBuffer();
      out.push(normalizeBullet(line));
      continue;
    }

    // Si la ligne suivante est un "fragment" de phrase, on la recolle
    // Heuristique : on recolle si la ligne ne finit pas par ponctuation forte
    // et si la ligne suivante n’est pas un titre / puce.
    if (!buffer) {
      buffer = line;
    } else {
      const prevEndsStrong = /[.:;!?)]$/.test(buffer);
      if (!prevEndsStrong) {
        buffer += " " + line;
      } else {
        flushBuffer();
        buffer = line;
      }
    }
  }

  flushBuffer();

  // 2) Format final :
  // - Mettre une ligne vide avant les titres
  // - Garder les puces sur une ligne chacune
  const pretty: string[] = [];
  for (const part of out) {
    if (isTitleLine(part)) {
      if (pretty.length) pretty.push(""); // ligne vide avant titre
      pretty.push(part);
    } else {
      pretty.push(part);
    }
  }

  // Remove extra blank lines
  let final = pretty.join("\n").replace(/\n{3,}/g, "\n\n").trim();

  return final;
}