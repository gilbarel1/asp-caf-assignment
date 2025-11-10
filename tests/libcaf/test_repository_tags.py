"""Unit tests for tag operations in the Repository class."""

from pathlib import Path
from libcaf.repository import Repository, RepositoryError, TagError
from libcaf.constants import TAGS_DIR, REFS_DIR, DEFAULT_REPO_DIR
from pytest import raises, fixture


@fixture
def repo_with_commits(temp_repo: Repository) -> tuple[Repository, list[str]]:
    """Create a repository with multiple commits for testing."""
    commit_hashes = []
    
    # First commit
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('First commit content')
    commit1 = temp_repo.commit_working_dir('Tester', 'First commit')
    commit_hashes.append(commit1)
    
    # Second commit
    file1.write_text('Second commit content')
    commit2 = temp_repo.commit_working_dir('Tester', 'Second commit')
    commit_hashes.append(commit2)
    
    # Third commit
    file1.write_text('Third commit content')
    commit3 = temp_repo.commit_working_dir('Tester', 'Third commit')
    commit_hashes.append(commit3)
    
    return temp_repo, commit_hashes


def test_create_tag_at_head(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test creating a tag at the current HEAD."""
    repo, commits = repo_with_commits
    
    repo.create_tag('v1.0.0')
    
    # Verify tag file exists
    tag_path = repo.tags_dir() / 'v1.0.0'
    assert tag_path.exists()
    
    # Verify tag points to HEAD commit
    from libcaf.ref import read_ref
    tag_ref = read_ref(tag_path)
    assert tag_ref == commits[2]  # Should point to the latest commit


def test_create_tag_at_specific_commit(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test creating a tag at a specific commit."""
    repo, commits = repo_with_commits
    
    repo.create_tag('v0.1.0', commits[0])
    
    # Verify tag points to the first commit
    from libcaf.ref import read_ref
    tag_path = repo.tags_dir() / 'v0.1.0'
    tag_ref = read_ref(tag_path)
    assert tag_ref == commits[0]


def test_create_tag_empty_name_raises_error(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that creating a tag with an empty name raises ValueError."""
    repo, _ = repo_with_commits
    
    with raises(ValueError, match='Tag name is required'):
        repo.create_tag('')


def test_create_duplicate_tag_raises_error(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that creating a duplicate tag raises TagError."""
    repo, _ = repo_with_commits
    
    repo.create_tag('v1.0.0')
    
    with raises(TagError, match='Tag "v1.0.0" already exists'):
        repo.create_tag('v1.0.0')


def test_create_tag_invalid_commit_raises_error(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that creating a tag with an invalid commit raises RepositoryError."""
    repo, _ = repo_with_commits
    
    fake_commit = 'a' * 40  # Valid format but doesn't exist
    
    with raises(RepositoryError, match='does not exist'):
        repo.create_tag('v1.0.0', fake_commit)


def test_create_tag_in_empty_repo_raises_error(temp_repo: Repository) -> None:
    """Test that creating a tag in an empty repository raises RepositoryError."""
    with raises(RepositoryError, match='No commits in repository'):
        temp_repo.create_tag('v1.0.0')


def test_delete_tag(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test deleting a tag."""
    repo, _ = repo_with_commits
    
    repo.create_tag('v1.0.0')
    tag_path = repo.tags_dir() / 'v1.0.0'
    assert tag_path.exists()
    
    repo.delete_tag('v1.0.0')
    assert not tag_path.exists()


def test_delete_tag_empty_name_raises_error(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that deleting a tag with an empty name raises ValueError."""
    repo, _ = repo_with_commits
    
    with raises(ValueError, match='Tag name is required'):
        repo.delete_tag('')


def test_delete_nonexistent_tag_raises_error(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that deleting a non-existent tag raises TagError."""
    repo, _ = repo_with_commits
    
    with raises(TagError, match='Tag "nonexistent" does not exist'):
        repo.delete_tag('nonexistent')


def test_list_tags_empty(temp_repo: Repository) -> None:
    """Test listing tags when there are none."""
    # Create a commit so we can create tags
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content')
    temp_repo.commit_working_dir('Tester', 'Initial commit')
    
    tags = temp_repo.list_tags()
    assert tags == []


def test_list_tags_single(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test listing a single tag."""
    repo, commits = repo_with_commits
    
    repo.create_tag('v1.0.0', commits[2])
    
    tags = repo.list_tags()
    assert len(tags) == 1
    assert tags[0][0] == 'v1.0.0'
    assert tags[0][1] == commits[2]


def test_list_tags_multiple(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test listing multiple tags."""
    repo, commits = repo_with_commits
    
    repo.create_tag('v1.0.0', commits[2])
    repo.create_tag('v0.1.0', commits[0])
    repo.create_tag('v0.2.0', commits[1])
    
    tags = repo.list_tags()
    assert len(tags) == 3
    
    # Tags should be sorted alphabetically
    assert tags[0][0] == 'v0.1.0'
    assert tags[1][0] == 'v0.2.0'
    assert tags[2][0] == 'v1.0.0'
    
    # Verify commit associations
    assert tags[0][1] == commits[0]
    assert tags[1][1] == commits[1]
    assert tags[2][1] == commits[2]


def test_list_tags_no_tags_directory(temp_repo: Repository) -> None:
    """Test listing tags when tags directory doesn't exist."""
    # Create a commit so repository is valid
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content')
    temp_repo.commit_working_dir('Tester', 'Initial commit')
    
    # Ensure tags directory doesn't exist
    tags_dir = temp_repo.tags_dir()
    if tags_dir.exists():
        tags_dir.rmdir()
    
    tags = temp_repo.list_tags()
    assert tags == []


def test_tag_exists(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test checking if a tag exists."""
    repo, _ = repo_with_commits
    
    assert not repo.tag_exists('v1.0.0')
    
    repo.create_tag('v1.0.0')
    assert repo.tag_exists('v1.0.0')
    
    repo.delete_tag('v1.0.0')
    assert not repo.tag_exists('v1.0.0')


def test_tags_directory_created_automatically(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that tags directory is created automatically when creating a tag."""
    repo, _ = repo_with_commits
    
    # Ensure tags directory doesn't exist
    tags_dir = repo.tags_dir()
    if tags_dir.exists():
        import shutil
        shutil.rmtree(tags_dir)
    
    assert not tags_dir.exists()
    
    repo.create_tag('v1.0.0')
    assert tags_dir.exists()
    assert tags_dir.is_dir()


def test_create_tag_with_special_characters(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test creating tags with various naming conventions."""
    repo, _ = repo_with_commits
    
    # Test various valid tag names
    valid_names = ['v1.0.0', 'release-2023', 'feature_test', 'v1.0.0-beta']
    
    for name in valid_names:
        repo.create_tag(name)
        assert repo.tag_exists(name)


def test_tag_persists_across_repository_operations(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that tags persist even after new commits."""
    repo, commits = repo_with_commits
    
    # Create a tag at the second commit
    repo.create_tag('stable', commits[1])
    
    # Create more commits
    file1 = repo.working_dir / 'file1.txt'
    file1.write_text('Fourth commit content')
    commit4 = repo.commit_working_dir('Tester', 'Fourth commit')
    
    # Verify tag still exists and points to the same commit
    assert repo.tag_exists('stable')
    tags = repo.list_tags()
    stable_tag = next(t for t in tags if t[0] == 'stable')
    assert stable_tag[1] == commits[1]
    assert stable_tag[1] != commit4


def test_multiple_tags_same_commit(repo_with_commits: tuple[Repository, list[str]]) -> None:
    """Test that multiple tags can point to the same commit."""
    repo, commits = repo_with_commits
    
    # Create multiple tags pointing to the same commit
    repo.create_tag('v1.0.0', commits[2])
    repo.create_tag('latest', commits[2])
    repo.create_tag('production', commits[2])
    
    tags = repo.list_tags()
    assert len(tags) == 3
    
    # All should point to the same commit
    assert all(t[1] == commits[2] for t in tags)