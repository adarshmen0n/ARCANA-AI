/**
 * ARCANA-AI Shared TypeScript Type Definitions
 * Version: 1.0.0
 * 
 * Defines cross-language interfaces for Frontend (Jeenth) and Game Engine (Dasarth).
 */

export type DifficultyLevel = 1 | 2 | 3 | 4 | 5;

export type ChallengeType = 'mcq' | 'concept_puzzle' | 'boss_override' | 'calculation';

export type HintType = 'nudge' | 'guidance' | 'scaffold';

export interface NarrativePayload {
  zone_theme: string;
  mission_intro: string;
}

export interface NPCPayload {
  npc_id: string;
  npc_name: string;
  dialogue: string[];
  lore_snippet?: string;
}

export interface ChallengeOption {
  id: string;
  text: string;
}

export interface ProgressiveHint {
  level: 1 | 2 | 3;
  type: HintType;
  text: string;
}

export interface ChallengePayload {
  challenge_id: string;
  challenge_type: ChallengeType;
  prompt: string;
  options: ChallengeOption[];
  correct_option_id: string;
  hints: ProgressiveHint[];
  explanation: string;
}

export interface BossPayload {
  is_boss_mission: boolean;
  boss_id?: string | null;
  boss_name?: string | null;
  shield_weakness_concept?: string | null;
  phases: number;
}

export interface RewardPayload {
  xp: number;
  knowledge_coins: number;
  mastery_boost_potential: number;
}

export interface SpecificationMetadata {
  source_document_id?: string;
  chunk_ids: string[];
  generated_at: string;
  generator_model: string;
}

export interface GameSpecification {
  version: string;
  mission_id: string;
  concept_id: string;
  title: string;
  difficulty: DifficultyLevel;
  learning_objective: string;
  narrative: NarrativePayload;
  npc: NPCPayload;
  challenge: ChallengePayload;
  boss: BossPayload;
  reward: RewardPayload;
  metadata: SpecificationMetadata;
}

export type GameEventType =
  | 'QUESTION_STARTED'
  | 'QUESTION_ANSWERED'
  | 'HINT_REQUESTED'
  | 'MISSION_STARTED'
  | 'MISSION_COMPLETED'
  | 'MISSION_FAILED'
  | 'NPC_INTERACTION'
  | 'BOSS_STARTED'
  | 'BOSS_COMPLETED'
  | 'PLAYER_DIED';

export interface EventPayload {
  challenge_id?: string;
  selected_option_id?: string;
  is_correct?: boolean;
  difficulty: DifficultyLevel;
  time_taken_seconds: number;
  hints_used_count: number;
  highest_hint_level: number;
  remaining_player_health: number;
  attempt_number: number;
}

export interface GameEvent {
  version: string;
  event_id: string;
  student_id: string;
  session_id: string;
  mission_id: string;
  concept_id: string;
  event_type: GameEventType;
  payload: EventPayload;
  client_timestamp: string;
}

export interface ConceptMastery {
  concept_id: string;
  mastery_score: number;
  total_attempts: number;
  successful_attempts: number;
  consecutive_correct: number;
  last_attempt_timestamp?: string;
  last_difficulty_solved: DifficultyLevel;
}

export interface StudentProfile {
  student_id: string;
  display_name: string;
  xp: number;
  level: number;
  knowledge_coins: number;
  concept_mastery: Record<string, ConceptMastery>;
  completed_missions: string[];
  weak_concepts: string[];
  strong_concepts: string[];
}
