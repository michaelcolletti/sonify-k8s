/// Sonification module - maps metrics to sounds
pub mod mapper;
pub mod sound_map;

pub use mapper::{calculate_index, get_color, map_metric};
pub use sound_map::{get_sound_map, MetricConfig, Note};
