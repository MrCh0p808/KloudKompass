# StatWoX Database Schema (Current Status)

This document represents the canonical database structure as of Wave 6.4.

## Core Models

### User
The central identity model.
- **Fields**: `email`, `passwordHash`, `username`, `name`, `image`, `isVerified`.
- **Identity**: Supports `googleId`, `linkedInId`, `digilockerId`.
- **Security**: `twoFactorEnabled`, `twoFactorSecret`.
- **Usage**: Tracks `aiSentimentUsage` and `funnelViewUsage`.

### Survey
The primary container for research.
- **Fields**: `title`, `description`, `category`, `status`, `isPublic`.
- **Configuration**: `allowAnon`, `collectEmail`, `maxResponses`, `closesAt`.
- **Logic**: `thankYouLogic`, `theme` (JSON), `locale`.
- **Engagement**: `responseCount`, `viewCount`, `likeCount`, `commentCount`.

### Question
Individual data collection points.
- **Types**: See `QuestionType` enum.
- **Structure**: `options` (JSON), `logic` (Skip logic JSON), `required`.
- **Matrix**: `rows` and `columns` labels (JSON).

### Response & Answer
The data collection layer.
- **Response**: Tracks `startedAt`, `completedAt`, `ipAddress`, `userAgent`.
- **Answer**: Stores `value`, `fileUrl`, `matrixData`, `rankingData`, and `sentimentScore`.

## Enum Definitions
- `SurveyStatus`: `draft`, `published`, `closed`.
- `QuestionType`: `shortText`, `longText`, `multipleChoice`, `dropdown`, `checkbox`, `rating`, `nps`, `matrix`, `ranking`, `fileUpload`, `date`, `email`, `phone`, `number`, `likert`, `yesNo`.
- `VerificationMethod`: `none`, `email`, `phone`, `digilocker`, `linkedin`, `google`.

## Security Models
- `RefreshToken`: Handles JWT rotation with `hashedToken`.
- `VerificationToken`: For email and password reset flows.
- `PasswordResetToken`: (Wave 6.4 Fix) Specifically for email resets via `tokenHash`.
- `OTP`: Simple verification codes.

## Advanced Features
- `Workspace`: Supports RBAC via `WorkspaceMember` and `WorkspaceRole`.
- `SurveyVersion`: Snapshots for survey history.
- `Template`: Marketplace blueprint structures.
- `PageView`: Funnel analytics tracking.
- `AuditLog`: Action tracking for compliance.
- `Report`: Content moderation system.