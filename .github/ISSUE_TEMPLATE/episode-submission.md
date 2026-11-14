---
name: Episode submission
title: "[EPISODE] S__E__ - Guest"
labels: submission
body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing. Attach the video file to this issue; a
        maintainer saves it, deletes the attachment from GitHub, and closes
        the issue once it is verified and in the archive.
  - type: input
    id: episode
    attributes:
      label: Season and episode
      placeholder: S06E10
    validations:
      required: true
  - type: input
    id: guest
    attributes:
      label: Guest name
      description: As listed on the Wikipedia episode list.
    validations:
      required: true
  - type: dropdown
    id: source
    attributes:
      label: Source
      options:
        - Broadcast
        - DVD
        - Streaming rip
        - Private collection
        - Unknown
    validations:
      required: true
  - type: input
    id: runtime
    attributes:
      label: Runtime
      placeholder: 41m 21s
  - type: input
    id: resolution
    attributes:
      label: Resolution
      placeholder: 768x576
  - type: textarea
    id: notes
    attributes:
      label: Notes
      description: Alternate cut, missing opening, audio issues, subtitles, etc.
