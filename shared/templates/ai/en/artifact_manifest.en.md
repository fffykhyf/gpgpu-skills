# Artifact Manifest

## Purpose

Record every English AI artifact and Chinese human report produced in a run.

## Required Fields

- `run_id`
- `output_mode`
- `ai_artifacts`
- `human_reports`

## Rules

- AI artifacts use `language: en-US`.
- Human reports use `language: zh-CN`.
- Every human report lists `source_artifacts`.
- Every AI artifact lists `producer_skill`, `visibility`, and `content_hash`.
