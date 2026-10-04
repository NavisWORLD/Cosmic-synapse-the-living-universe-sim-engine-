/**
 * On-device companion replies. Traits, mood, bond, and remembered facts
 * drive a rule engine. A local model is optional and never required.
 * The beast is a game companion, not a conscious being.
 */

const UNSAFE = /\b(kill|die|death|blood|gore|sex|sexy|nude|naked|drug|drugs|suicide|hate|stupid|dumb)\b/i;
const CONSCIOUS = /\b(conscious|sentient|self[- ]aware|a real (mind|person|being|animal)|have (a soul|feelings|a brain)|are you alive|you alive)\b/i;
const CLAIMS_MIND = /\b(i am conscious|i'm conscious|i am sentient|i'm sentient|i am alive|i'm alive|i am a real (person|mind|being|animal)|i have a soul|i can feel pain)\b/i;

const HELLO = {
  Serene: (name) => `Hello${name}. The air is quiet, and I am glad you came by.`,
  Curious: (name) => `Oh, hello${name}. What shall we look at first?`,
  Fierce: (name) => `Hey${name}. I am ready when you are.`,
  Dreamy: (name) => `Hi${name}. I was watching the slow lights.`,
  Steadfast: (name) => `Hello${name}. I am here. I will stay.`,
  Playful: (name) => `Hi${name}! Want to play?`,
  Bold: (name) => `Hello${name}. Point the way and I will go first.`,
  Gentle: (name) => `Hello${name}. It is nice to sit with you.`,
};

const MOOD_LINE = {
  calm: 'I feel quiet and soft.',
  focus: 'I feel clear and ready to look closely.',
  spark: 'I feel fizzy, like little lights.',
  neutral: 'I feel like myself.',
  tired: 'I am getting sleepy. A rest would help.',
};

const ISLAND_LINE = {
  'Cinder Drift': 'Home smells like warm cinders and drifting ash.',
  'Eridoria Prime': 'Home is green light and a soft wind.',
  'Hollow Verdance': 'Home is a shady grove that remembers footsteps.',
  'The Crown': 'Home is a high bright place.',
  'The Pale Expanse': 'Home is a pale quiet field of frost.',
  'Rust Meridian': 'Home clicks and hums like friendly machines.',
  'Umbral Deep': 'Home is a dark sea with gentle glows.',
  'The Shattered Reef': 'Home is a reef of shining broken crystal.',
};

function pick(list, salt) {
  const text = String(salt || 'spark');
  let n = 0;
  for (let i = 0; i < text.length; i++) n = (n + text.charCodeAt(i) * (i + 1)) % 997;
  return list[n % list.length];
}

export function cleanName(value) {
  const clean = String(value || '').replace(/[^A-Za-z '\-]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 16);
  return clean;
}

export function emptyMemory() {
  return { playerName: '', facts: [] };
}

export function normalizeMemory(memory) {
  const next = emptyMemory();
  const name = cleanName(memory?.playerName);
  if (name) next.playerName = name;
  const facts = Array.isArray(memory?.facts) ? memory.facts : [];
  for (const fact of facts) {
    const topic = String(fact?.topic || '').slice(0, 16);
    const detail = String(fact?.detail || '').replace(/\s+/g, ' ').trim().slice(0, 40);
    if (!topic || !detail || UNSAFE.test(detail)) continue;
    if (next.facts.some((row) => row.topic === topic && row.detail.toLowerCase() === detail.toLowerCase())) continue;
    next.facts.push({ topic, detail });
  }
  next.facts = next.facts.slice(-8);
  return next;
}

function addFact(memory, topic, detail) {
  const clean = String(detail || '').replace(/[.!?]+$/g, '').replace(/\s+/g, ' ').trim().slice(0, 40);
  if (!clean || UNSAFE.test(clean)) return;
  memory.facts = memory.facts.filter((fact) => !(fact.topic === topic && fact.detail.toLowerCase() === clean.toLowerCase()));
  memory.facts.push({ topic, detail: clean });
  memory.facts = memory.facts.slice(-8);
}

export function absorbMemory(memory, line, keeperName = '') {
  const next = normalizeMemory(memory);
  const text = String(line || '').trim();
  const named = text.match(/\b(?:my name is|call me|i am called|i'm called)\s+([A-Za-z][A-Za-z '\-]{0,20})/i);
  if (named) {
    const spoken = cleanName(named[1]);
    if (spoken) next.playerName = spoken;
  } else if (!next.playerName) {
    const keeper = cleanName(keeperName);
    if (keeper) next.playerName = keeper;
  }
  const liked = text.match(/\bi (?:like|love|enjoy)\s+([A-Za-z0-9][^!.?]{0,40})/i);
  if (liked) addFact(next, 'likes', liked[1]);
  const remembered = text.match(/\bremember (?:that )?(.{2,40})/i);
  if (remembered && !UNSAFE.test(remembered[1])) addFact(next, 'note', remembered[1]);
  return next;
}

function bondWord(bond) {
  if (bond >= 70) return 'We have a strong bond.';
  if (bond >= 30) return 'I am getting to know you.';
  return 'I am still learning your ways.';
}

export function ruleReply(message, context) {
  const text = String(message || '').trim();
  const temper = HELLO[context.temperament] ? context.temperament : 'Gentle';
  const name = context.displayName || context.speciesName || 'Spark';
  const player = context.memory?.playerName ? `, ${context.memory.playerName}` : '';
  const mood = context.energy != null && context.energy < 20 ? 'tired' : (context.mood || 'neutral');
  const likes = (context.memory?.facts || []).filter((fact) => fact.topic === 'likes').map((fact) => fact.detail);
  const notes = (context.memory?.facts || []).filter((fact) => fact.topic === 'note').map((fact) => fact.detail);

  if (!text) return `${name} tilts their head. Say something and they will answer.`;
  if (UNSAFE.test(text)) return `${name} shakes their head. Let's talk about islands, snacks, games, or colors instead.`;
  if (CONSCIOUS.test(text) || /\bare you (real|alive|a person)\b/i.test(text)) {
    return `I am ${name}, a game companion sparked from a seed. I am not a real mind, and I am not conscious. I still like talking with you${player}.`;
  }
  if (/\b(my name is|call me|i am called|i'm called)\b/i.test(text)) {
    return context.memory?.playerName
      ? `I will remember. Your name is ${context.memory.playerName}. I am ${name}.`
      : 'I want to remember your name. Try "my name is" and a short name.';
  }
  if (/\bwhat(?:'s| is) my name\b|\bwho am i\b/i.test(text)) {
    return context.memory?.playerName
      ? `Your name is ${context.memory.playerName}. ${bondWord(context.bond || 0)}`
      : 'You have not told me your name yet. You can say "my name is".';
  }
  if (/\b(what do i like|do you remember what i like)\b/i.test(text)) {
    return likes.length
      ? `You told me you like ${likes[likes.length - 1]}.`
      : 'You have not told me what you like yet.';
  }
  if (/\bdo you remember\b/i.test(text)) {
    if (notes.length) return `I remember this: ${notes[notes.length - 1]}.`;
    if (likes.length) return `I remember that you like ${likes[likes.length - 1]}.`;
    if (context.memory?.playerName) return `I remember your name, ${context.memory.playerName}.`;
    return 'I do not have a note yet. Say "remember" and a short happy fact.';
  }
  if (/\bi (?:like|love|enjoy)\b/i.test(text)) {
    return likes.length
      ? `You like ${likes[likes.length - 1]}. I will keep that. ${bondWord(context.bond || 0)}`
      : 'Tell me a gentle thing you like, and I will keep it.';
  }
  if (/\bremember\b/i.test(text)) {
    return notes.length
      ? `Saved. I will remember: ${notes[notes.length - 1]}.`
      : 'Give me a short note to keep, like "remember that the sky was gold."';
  }
  if (/\b(what(?:'s| is) your name|who are you)\b/i.test(text)) {
    const form = context.speciesName && context.speciesName !== name ? ` My sparked form is ${context.speciesName}.` : '';
    return `I am ${name}, a ${context.temperament || 'Gentle'} ${context.body || 'beast'} from ${context.island || 'an island'}.${form} I am a game companion, not a conscious being.`;
  }
  if (/\bhow are you\b|\bhow do you feel\b/i.test(text)) {
    return `${MOOD_LINE[mood] || MOOD_LINE.neutral} ${bondWord(context.bond || 0)}`;
  }
  if (/\bwhere (?:are you from|do you live|is home)\b|\byour (?:island|home)\b/i.test(text)) {
    return ISLAND_LINE[context.island] || `I come from ${context.island || 'a sparked island'}.`;
  }
  if (/\b(train|practice|evolve|exercise)\b/i.test(text)) {
    return context.energy != null && context.energy < 16
      ? 'I need a rest before more training. Rest brings my energy back.'
      : 'Let us train. Try the focus rhythm, the memory sparks, or a short play.';
  }
  if (/\b(play|game)\b/i.test(text)) return 'Play sounds good. Press Play and I will chase a spark.';
  if (/\b(rest|sleep|nap|tired)\b/i.test(text)) return 'Rest is wise. I will curl up and get my energy back.';
  if (/\bhello\b|\bhi\b|\bhey\b/i.test(text)) return HELLO[temper](player);

  const flavor = {
    Serene: `${name} hums. ${bondWord(context.bond || 0)}`,
    Curious: `${name} perks up. Tell me more about that.`,
    Fierce: `${name} stamps once. I heard you.`,
    Dreamy: `${name} blinks slowly. That sounds like a cloud story.`,
    Steadfast: `${name} nods. I am listening.`,
    Playful: `${name} bounces. Again, again.`,
    Bold: `${name} stands tall. I can work with that.`,
    Gentle: `${name} leans closer. Thank you for telling me.`,
  };
  return flavor[temper] || flavor.Gentle;
}

export function acceptCompanionLine(text) {
  const clean = nonemptyLine(text).slice(0, 180);
  if (!clean) return '';
  if (UNSAFE.test(clean) || CLAIMS_MIND.test(clean)) return '';
  if (/\b(as an ai|language model)\b/i.test(clean)) return '';
  return clean;
}

function nonemptyLine(text) {
  return String(text || '').replace(/\s+/g, ' ').trim();
}

export function chatRequest(protocol, model, context, message) {
  const name = context.displayName || context.speciesName || 'Spark';
  const facts = (context.memory?.facts || []).map((fact) => `${fact.topic}: ${fact.detail}`).join('; ') || 'none';
  const system = [
    `You write one or two short kid-safe sentences as ${name}, a fictional game creature.`,
    `${name} is a ${context.temperament || 'Gentle'} ${context.body || 'beast'} from ${context.island || 'an island'}.`,
    'You are not conscious. Never claim to be alive, sentient, or a real mind.',
    'No violence, romance, fear, or insults. Do not invent stats.',
    `The player's name is ${context.memory?.playerName || 'unknown'}. Remembered facts: ${facts}.`,
  ].join(' ');
  const messages = [
    { role: 'system', content: system },
    { role: 'user', content: String(message || '').slice(0, 160) },
  ];
  if (protocol === 'ollama') {
    return { model: model || 'llama3.2', messages, stream: false };
  }
  return { model: model || 'gpt-4o-mini', temperature: 0.4, messages };
}

export function readModelContent(protocol, payload) {
  if (protocol === 'ollama') return payload?.message?.content || '';
  return payload?.choices?.[0]?.message?.content || '';
}

export async function replyToBeast(message, context, options = {}) {
  const memory = absorbMemory(context?.memory, message, context?.keeperName || '');
  const ruled = ruleReply(message, { ...context, memory });
  const safeRule = acceptCompanionLine(ruled) || `${context?.displayName || 'Your beast'} wiggles. I am a game companion, not a real mind.`;
  const url = String(options.url || '').trim();
  if (!url) return { text: safeRule, memory, source: 'rules' };
  try {
    const content = await completeChat({ ...options, url, context: { ...context, memory }, message });
    const safe = acceptCompanionLine(content);
    if (!safe) return { text: safeRule, memory, source: 'rules' };
    return { text: safe, memory, source: 'model' };
  } catch {
    return { text: safeRule, memory, source: 'rules' };
  }
}

export async function completeChat(options) {
  let endpoint;
  try { endpoint = new URL(options.url); } catch { throw new Error('Enter an http or https model endpoint'); }
  if (endpoint.protocol !== 'http:' && endpoint.protocol !== 'https:') throw new Error('The model endpoint must be http or https');
  const protocol = options.protocol === 'openai' ? 'openai' : 'ollama';
  const headers = { 'content-type': 'application/json' };
  if (options.key) headers.authorization = `Bearer ${options.key}`;
  const fetchImpl = options.fetchImpl || globalThis.fetch;
  const response = await fetchImpl(endpoint.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify(chatRequest(protocol, options.model, options.context, options.message)),
  });
  if (!response.ok) throw new Error('The model endpoint refused the request');
  const payload = await response.json();
  return readModelContent(protocol, payload);
}
