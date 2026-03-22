
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { Rating } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getScoreColor(score: number): string {
  if (score >= 8.5) return 'text-emerald-400'
  if (score >= 7.0) return 'text-blue-400'
  if (score >= 5.0) return 'text-yellow-400'
  return 'text-red-400'
}

export function getScoreBgColor(score: number): string {
  if (score >= 8.5) return 'bg-emerald-400'
  if (score >= 7.0) return 'bg-blue-400'
  if (score >= 5.0) return 'bg-yellow-400'
  return 'bg-red-400'
}

export function getRatingColor(rating: Rating): string {
  switch (rating) {
    case 'excellent': return 'text-emerald-400'
    case 'good': return 'text-blue-400'
    case 'needs_improvement': return 'text-yellow-400'
    case 'poor': return 'text-red-400'
    default: return 'text-gray-400'
  }
}

export function getRatingBadgeClass(rating: Rating): string {
  switch (rating) {
    case 'excellent': return 'bg-emerald-400/10 text-emerald-400 border-emerald-400/30'
    case 'good': return 'bg-blue-400/10 text-blue-400 border-blue-400/30'
    case 'needs_improvement': return 'bg-yellow-400/10 text-yellow-400 border-yellow-400/30'
    case 'poor': return 'bg-red-400/10 text-red-400 border-red-400/30'
    default: return 'bg-gray-400/10 text-gray-400 border-gray-400/30'
  }
}

export function getRatingEmoji(rating: Rating): string {
  switch (rating) {
    case 'excellent': return '🏆'
    case 'good': return '✅'
    case 'needs_improvement': return '📈'
    case 'poor': return '📚'
    default: return '❓'
  }
}

export function formatLevel(level: string): string {
  switch (level) {
    case 'fresher': return 'Fresher (0-1 years)'
    case 'mid': return 'Mid Level (2-4 years)'
    case 'senior': return 'Senior (5+ years)'
    default: return level
  }
}

export function formatInterviewType(type: string): string {
  switch (type) {
    case 'technical': return 'Technical'
    case 'hr': return 'HR'
    case 'behavioral': return 'Behavioral'
    case 'system_design': return 'System Design'
    default: return type
  }
}

export function formatDifficulty(difficulty: string): string {
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function getAxisLabel(axis: string): string {
  switch (axis) {
    case 'technical': return 'Technical Accuracy'
    case 'depth': return 'Depth'
    case 'clarity': return 'Clarity'
    case 'relevance': return 'Relevance'
    case 'structure': return 'Structure'
    default: return axis
  }
}