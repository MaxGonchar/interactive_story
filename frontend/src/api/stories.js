const STORIES = [
  {
    id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
    title: "The Black Harbor",
  },
  {
    id: "b3c2d1e0-1234-4abc-89de-f01234567890",
    title: "The Forgotten Citadel",
  },
];

const STORIES_DETAIL = {
  "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8": {
    id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
    title: "The Black Harbor",
    scenes: [
      { id: 1, finished: true },
      { id: 2, finished: true },
      { id: 3, finished: false },
    ],
    active_scene_id: 3,
  },
  "b3c2d1e0-1234-4abc-89de-f01234567890": {
    id: "b3c2d1e0-1234-4abc-89de-f01234567890",
    title: "The Forgotten Citadel",
    scenes: [
      { id: 1, finished: true },
      { id: 2, finished: false },
      { id: 3, finished: false },
    ],
    active_scene_id: 2,
  },
};

export async function getStories() {
  return { data: STORIES };
}

export async function getStory(storyId) {
  return { data: STORIES_DETAIL[storyId] };
}
