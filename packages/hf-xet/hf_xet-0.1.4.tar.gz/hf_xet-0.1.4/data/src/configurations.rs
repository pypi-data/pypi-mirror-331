use std::path::{Path, PathBuf};
use std::str::FromStr;

use cas_client::CacheConfig;
use cas_object::CompressionScheme;
use utils::auth::AuthConfig;

use crate::errors::Result;
use crate::repo_salt::RepoSalt;

#[derive(Debug)]
pub enum Endpoint {
    Server(String),
    FileSystem(PathBuf),
}

#[derive(Debug)]
pub struct StorageConfig {
    pub endpoint: Endpoint,
    pub compression: Option<CompressionScheme>,
    pub auth: Option<AuthConfig>,
    pub prefix: String,
    pub cache_config: Option<CacheConfig>,
    pub staging_directory: Option<PathBuf>,
}

#[derive(Debug)]
pub struct DedupConfig {
    pub repo_salt: Option<RepoSalt>,
    pub global_dedup_policy: GlobalDedupPolicy,
}

#[derive(Debug)]
pub struct RepoInfo {
    pub repo_paths: Vec<String>,
}

#[derive(PartialEq, Default, Clone, Debug, Copy)]
pub enum FileQueryPolicy {
    /// Query local first, then the shard server.
    #[default]
    LocalFirst,

    /// Only query the server; ignore local shards.
    ServerOnly,

    /// Only query local shards.
    LocalOnly,
}

impl FromStr for FileQueryPolicy {
    type Err = std::io::Error;

    fn from_str(s: &str) -> std::result::Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "local_first" => Ok(FileQueryPolicy::LocalFirst),
            "server_only" => Ok(FileQueryPolicy::ServerOnly),
            "local_only" => Ok(FileQueryPolicy::LocalOnly),
            _ => Err(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                format!("Invalid file smudge policy, should be one of local_first, server_only, local_only: {}", s),
            )),
        }
    }
}

#[derive(PartialEq, Default, Clone, Debug, Copy)]
pub enum GlobalDedupPolicy {
    /// Never query for new shards using chunk hashes.
    Never,

    /// Always query for new shards by chunks
    #[default]
    Always,
}

impl FromStr for GlobalDedupPolicy {
    type Err = std::io::Error;

    fn from_str(s: &str) -> std::result::Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "never" => Ok(GlobalDedupPolicy::Never),
            "always" => Ok(GlobalDedupPolicy::Always),
            _ => Err(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                format!("Invalid global dedup query policy, should be one of never, direct_only, always: {}", s),
            )),
        }
    }
}

#[derive(Debug)]
pub struct TranslatorConfig {
    pub file_query_policy: FileQueryPolicy,
    pub cas_storage_config: StorageConfig,
    pub shard_storage_config: StorageConfig,
    pub dedup_config: Option<DedupConfig>,
    pub repo_info: Option<RepoInfo>,
}

impl TranslatorConfig {
    pub fn local_config(base_dir: impl AsRef<Path>, enable_dedup: bool) -> Result<Self> {
        let path = base_dir.as_ref().join("xet");
        std::fs::create_dir_all(&path)?;

        let translator_config = Self {
            file_query_policy: Default::default(),
            cas_storage_config: StorageConfig {
                endpoint: Endpoint::FileSystem(path.join("xorbs")),
                compression: Default::default(),
                auth: None,
                prefix: "default".into(),
                cache_config: Some(CacheConfig {
                    cache_directory: path.join("cache"),
                    cache_size: 10 * 1024 * 1024 * 1024, // 10 GiB
                }),
                staging_directory: None,
            },
            shard_storage_config: StorageConfig {
                endpoint: Endpoint::FileSystem(path.join("xorbs")),
                compression: Default::default(),
                auth: None,
                prefix: "default-merkledb".into(),
                cache_config: Some(CacheConfig {
                    cache_directory: path.join("shard-cache"),
                    cache_size: 0, // ignored
                }),
                staging_directory: Some(path.join("shard-session")),
            },
            dedup_config: {
                if enable_dedup {
                    Some(DedupConfig {
                        repo_salt: None,
                        global_dedup_policy: Default::default(),
                    })
                } else {
                    None
                }
            },
            repo_info: Some(RepoInfo {
                repo_paths: vec!["".into()],
            }),
        };

        translator_config.validate()?;

        Ok(translator_config)
    }

    pub fn validate(&self) -> Result<()> {
        if let Endpoint::FileSystem(path) = &self.cas_storage_config.endpoint {
            std::fs::create_dir_all(path)?;
        }
        if let Some(cache) = &self.cas_storage_config.cache_config {
            std::fs::create_dir_all(&cache.cache_directory)?;
        }
        if let Some(path) = &self.cas_storage_config.staging_directory {
            std::fs::create_dir_all(path)?;
        }

        if let Endpoint::FileSystem(path) = &self.shard_storage_config.endpoint {
            std::fs::create_dir_all(path)?;
        }
        if let Some(cache) = &self.shard_storage_config.cache_config {
            std::fs::create_dir_all(&cache.cache_directory)?;
        }
        if let Some(path) = &self.shard_storage_config.staging_directory {
            std::fs::create_dir_all(path)?;
        }

        Ok(())
    }
}
