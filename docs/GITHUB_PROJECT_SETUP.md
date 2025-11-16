# GitHub Project Board Setup Guide

## Overview

This guide outlines how to set up and configure a GitHub Project Board for tracking the AI Model Catalog CLI development progress. The project board will help manage tasks, track milestones, and provide visibility into team progress.

## Project Board Configuration

### Board Type
- **Template**: Automated kanban
- **Visibility**: Public (for transparency)
- **Organization**: CS450_Team_Repo

### Board Structure

#### Columns
1. **Backlog** - Future tasks and ideas
2. **To Do** - Ready to start tasks
3. **In Progress** - Currently being worked on
4. **In Review** - Completed, awaiting review
5. **Done** - Completed and verified

#### Labels
- `critical` - Critical for auto-grader compatibility
- `required` - Required for assignment completion
- `enhancement` - Nice to have improvements
- `bug` - Bug fixes
- `documentation` - Documentation tasks
- `testing` - Testing related tasks
- `frontend` - CLI interface tasks
- `backend` - Core functionality tasks
- `api` - API integration tasks
- `metrics` - Scoring algorithm tasks

## Initial Issues and Tasks

### Critical Issues (Priority 1)

#### Issue 1: NDJSON Output Format
- **Title**: Implement NDJSON output format for auto-grader compatibility
- **Description**: Add `--format ndjson` option to CLI commands that outputs data in the exact format required by the auto-grader
- **Labels**: `critical`, `frontend`, `api`
- **Assignee**: Fahd
- **Estimated Time**: 2-3 hours
- **Acceptance Criteria**:
  - [ ] Add `--format` parameter to CLI commands
  - [ ] Implement NDJSON output format
  - [ ] Include all required fields from Table 1
  - [ ] Add latency measurements in milliseconds
  - [ ] Test with sample URLs

#### Issue 2: Size Score Object Format
- **Title**: Convert size score from float to hardware mapping object
- **Description**: Change size score to return object with hardware compatibility scores
- **Labels**: `critical`, `metrics`, `backend`
- **Assignee**: Ali
- **Estimated Time**: 1-2 hours
- **Acceptance Criteria**:
  - [ ] Modify size score to return object format
  - [ ] Include raspberry_pi, jetson_nano, desktop_pc, aws_server
  - [ ] Update tests to verify object format
  - [ ] Update documentation

#### Issue 3: Latency Measurements
- **Title**: Add timing measurements for each metric component
- **Description**: Measure and report latency for each metric calculation
- **Labels**: `critical`, `metrics`, `backend`
- **Assignee**: Ali
- **Estimated Time**: 1-2 hours
- **Acceptance Criteria**:
  - [ ] Add timing to each metric calculation
  - [ ] Report latency in milliseconds
  - [ ] Include in NDJSON output
  - [ ] Update tests

### Required Issues (Priority 2)

#### Issue 4: Local Repository Analysis ✅
- **Title**: Implement local repository analysis using Git library
- **Description**: Clone and analyze model repositories locally without using shell commands
- **Labels**: `required`, `backend`, `api`
- **Assignee**: Ethan
- **Estimated Time**: 4-6 hours
- **Acceptance Criteria**:
  - [x] Use Git library (not shell commands)
  - [x] Clone repositories locally
  - [x] Analyze Git metadata programmatically
  - [x] Inspect config.json, model_index.json, README.md
  - [x] Check model weights and tokenizer files
  - [x] Add tests for local analysis

#### Issue 5: LLM Integration for README Analysis ✅
- **Title**: Integrate LLM for enhanced README analysis
- **Description**: Use Purdue GenAI Studio API to analyze README content
- **Labels**: `required`, `metrics`, `backend`
- **Assignee**: Taiwo
- **Estimated Time**: 3-4 hours
- **Acceptance Criteria**:
  - [x] Set up Purdue GenAI Studio API integration
  - [x] Implement README analysis with LLM
  - [x] Enhance metrics with LLM insights
  - [x] Add error handling and fallbacks
  - [x] Add tests for LLM integration
  - [x] Document LLM usage

#### Issue 6: GitHub Project Board Setup (Optional)
- **Title**: Set up GitHub Project Board for progress tracking
- **Description**: Create and configure project board with initial issues
- **Labels**: `optional`, `documentation`
- **Assignee**: Fahd
- **Estimated Time**: 1 hour
- **Acceptance Criteria**:
  - [ ] Create GitHub Project Board
  - [ ] Configure columns and labels
  - [ ] Add initial issues and tasks
  - [ ] Assign team members to tasks
  - [ ] Set up automation rules

### Enhancement Issues (Priority 3)

#### Issue 7: Performance Optimization
- **Title**: Optimize performance for large models
- **Description**: Improve response times and memory usage
- **Labels**: `enhancement`, `backend`, `performance`
- **Assignee**: Ethan
- **Estimated Time**: 2-3 hours

#### Issue 8: Enhanced Error Messages
- **Title**: Improve error messages and user experience
- **Description**: Make error messages more helpful and user-friendly
- **Labels**: `enhancement`, `frontend`, `ux`
- **Assignee**: Fahd
- **Estimated Time**: 1-2 hours

#### Issue 9: Additional Test Coverage
- **Title**: Add more comprehensive test cases
- **Description**: Increase test coverage and add edge cases
- **Labels**: `enhancement`, `testing`
- **Assignee**: Taiwo
- **Estimated Time**: 2-3 hours

## Automation Rules

### Auto-move Rules
1. **When issue is assigned** → Move to "In Progress"
2. **When PR is created** → Move to "In Review"
3. **When PR is merged** → Move to "Done"

### Auto-label Rules
1. **Issues with "critical" in title** → Add `critical` label
2. **Issues with "bug" in title** → Add `bug` label
3. **Issues with "test" in title** → Add `testing` label

## Milestone Tracking

### Milestone 1: Auto-Grader Compatibility (Week 4)
- **Target Date**: Sept 24, 2024
- **Issues**: #1, #2, #3
- **Status**: In Progress

### Milestone 2: Required Features (Week 4-5)
- **Target Date**: Sept 26, 2024
- **Issues**: #4, #5, #6
- **Status**: Pending

### Milestone 3: Final Delivery (Week 5)
- **Target Date**: Sept 28, 2025
- **Issues**: All remaining
- **Status**: Pending

## Team Workflow

### Daily Standups
- **Time**: 15 minutes
- **Format**: Update project board, discuss blockers
- **Questions**:
  - What did you complete yesterday?
  - What are you working on today?
  - Any blockers or help needed?

### Weekly Reviews
- **Time**: 1 hour
- **Format**: Review progress, plan next week
- **Activities**:
  - Review completed tasks
  - Update time estimates
  - Identify risks and blockers
  - Plan next week's priorities

### Code Reviews
- **Process**: All PRs require review
- **Reviewers**: At least one team member
- **Criteria**: Code quality, tests, documentation

## Progress Tracking

### Metrics to Track
1. **Issues Completed** - Number of issues moved to "Done"
2. **Time Estimates** - Actual vs estimated time
3. **Bug Count** - Number of bugs found and fixed
4. **Test Coverage** - Percentage of code covered by tests
5. **Documentation** - Completeness of documentation

### Weekly Reports
- **Format**: Screenshot of project board + summary
- **Content**:
  - Completed tasks
  - Time spent by each member
  - Blockers and risks
  - Next week's plan

## Setup Instructions

### Step 1: Create Project Board
1. Go to GitHub repository
2. Click "Projects" tab
3. Click "New project"
4. Select "Automated kanban" template
5. Name: "AI Model Catalog CLI Development"
6. Set visibility to "Public"

### Step 2: Configure Columns
1. Rename columns as specified above
2. Add "In Review" column between "In Progress" and "Done"
3. Set up column descriptions

### Step 3: Create Labels
1. Go to repository settings
2. Click "Labels" in left sidebar
3. Create all labels listed above
4. Set appropriate colors for each label

### Step 4: Create Initial Issues
1. Create issues for each task listed above
2. Assign appropriate labels
3. Assign team members
4. Set milestones
5. Add detailed descriptions and acceptance criteria

### Step 5: Set Up Automation
1. Go to project board settings
2. Click "Workflows"
3. Enable automation rules
4. Configure auto-move and auto-label rules

### Step 6: Team Onboarding
1. Share project board link with team
2. Explain workflow and processes
3. Set up regular meeting schedule
4. Create communication channels

## Best Practices

### Issue Management
- **Clear Titles**: Use descriptive, actionable titles
- **Detailed Descriptions**: Include context, requirements, and acceptance criteria
- **Regular Updates**: Update progress and add comments
- **Close When Done**: Move to "Done" and close issues

### Time Tracking
- **Realistic Estimates**: Base estimates on past experience
- **Update Estimates**: Adjust as you learn more
- **Track Actual Time**: Record time spent for future estimates
- **Buffer Time**: Add 20% buffer to estimates

### Communication
- **Use Comments**: Update issues with progress and questions
- **Mention Team Members**: Use @username for notifications
- **Link Related Issues**: Reference related issues and PRs
- **Document Decisions**: Record important decisions in issue comments

## Current Project Status (January 2025)

### Completed Features ✅
- **Core CLI Functionality**: All basic commands implemented
- **Auto-Grader Interface**: `./run` script with URL processing
- **NDJSON Output Format**: Machine-readable output for automated evaluation
- **Size Score Object Format**: Hardware compatibility mapping
- **Local Repository Analysis**: Git integration with filesystem scanning
- **URL Processing**: Fixed parameter issues for auto-grader compatibility
- **Test Suite**: 101 tests with >80% coverage
- **Documentation**: Comprehensive API and usage documentation
- **LLM Integration**: README analysis using Purdue GenAI Studio API
- **Enhanced Metrics**: Intelligent analysis with LLM fallback
- **Performance Optimization**: Caching and rate limiting
- **Error Handling**: Comprehensive error recovery and fallback

### In Progress 🔄
- **Final Documentation Review**: Comprehensive documentation updates

### Pending Tasks ⏳
- **GitHub Project Board Setup**: Optional project management board
- **Postmortem Report**: Project completion analysis

### Project Completion: 98%
- **Critical Features**: 100% Complete
- **Required Features**: 100% Complete (LLM integration completed)
- **Documentation**: 98% Complete
- **Testing**: 95% Complete

### Next Priority Tasks
1. **Final Documentation Review** (1 hour) - In Progress
2. **GitHub Project Board Setup** (1 hour) - Optional
3. **Postmortem Report** (1 hour) - Pending

## Troubleshooting

### Common Issues
1. **Issues not auto-moving**: Check automation rules
2. **Labels not applying**: Verify label names match exactly
3. **Team members not seeing updates**: Check notification settings
4. **Milestones not updating**: Ensure issues are assigned to milestones

### Getting Help
- **GitHub Documentation**: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **Team Communication**: Use Discord/Slack for quick questions
- **Office Hours**: Attend course staff office hours for complex issues

---

**Note**: This project board setup follows GitHub best practices and is designed to support the CS450 assignment requirements for project management and progress tracking.
