"""CLI command tests for tag operations."""

from pathlib import Path
from collections.abc import Callable
from libcaf.repository import Repository
from libcaf.constants import DEFAULT_REPO_DIR, TAGS_DIR, REFS_DIR
from pytest import CaptureFixture, fixture

# Import will be: from caf import cli_commands
# For testing purposes, we'll assume cli_commands module exists


@fixture
def repo_with_commits(temp_repo: Repository, parse_commit_hash: Callable[[], str], 
                      capsys: CaptureFixture[str]) -> tuple[Repository, list[str]]:
    """Create a repository with multiple commits for CLI testing."""
    commit_hashes = []
    
    # First commit
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('First commit content')
    # Assuming cli_commands.commit exists
    # cli_commands.commit(working_dir_path=temp_repo.working_dir, 
    #                    author='Tester', message='First commit')
    commit1 = temp_repo.commit_working_dir('Tester', 'First commit')
    commit_hashes.append(str(commit1))
    capsys.readouterr()  # Clear output
    
    # Second commit
    file1.write_text('Second commit content')
    commit2 = temp_repo.commit_working_dir('Tester', 'Second commit')
    commit_hashes.append(str(commit2))
    capsys.readouterr()
    
    return temp_repo, commit_hashes


def test_create_tag_at_head(repo_with_commits: tuple[Repository, list[str]], 
                            capsys: CaptureFixture[str]) -> None:
    """Test creating a tag at HEAD via CLI."""
    from caf import cli_commands
    
    repo, commits = repo_with_commits
    
    assert cli_commands.create_tag(working_dir_path=repo.working_dir, 
                                   tag_name='v1.0.0', commit=None) == 0
    
    output = capsys.readouterr().out
    assert 'Tag "v1.0.0" created' in output
    assert commits[1] in output  # Should reference the HEAD commit
    
    # Verify tag file exists
    tag_path = repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / 'v1.0.0'
    assert tag_path.exists()


def test_create_tag_at_specific_commit(repo_with_commits: tuple[Repository, list[str]], 
                                       capsys: CaptureFixture[str]) -> None:
    """Test creating a tag at a specific commit via CLI."""
    from caf import cli_commands
    
    repo, commits = repo_with_commits
    
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='v0.1.0', commit=commits[0]) == 0
    
    output = capsys.readouterr().out
    assert 'Tag "v0.1.0" created' in output
    assert commits[0] in output


def test_create_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    """Test creating a tag when no repository exists."""
    from caf import cli_commands
    
    assert cli_commands.create_tag(working_dir_path=temp_repo_dir,
                                   tag_name='v1.0.0', commit=None) == -1
    
    assert 'No repository found' in capsys.readouterr().err


def test_create_tag_empty_name(repo_with_commits: tuple[Repository, list[str]], 
                               capsys: CaptureFixture[str]) -> None:
    """Test creating a tag with an empty name."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='', commit=None) == -1
    
    assert 'Tag name is required' in capsys.readouterr().err


def test_create_tag_duplicate(repo_with_commits: tuple[Repository, list[str]], 
                              capsys: CaptureFixture[str]) -> None:
    """Test creating a duplicate tag."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    # Create first tag
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='v1.0.0', commit=None) == 0
    capsys.readouterr()  # Clear output
    
    # Try to create duplicate
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='v1.0.0', commit=None) == -1
    
    assert 'already exists' in capsys.readouterr().err


def test_create_tag_invalid_commit(repo_with_commits: tuple[Repository, list[str]], 
                                   capsys: CaptureFixture[str]) -> None:
    """Test creating a tag with an invalid commit hash."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    fake_commit = 'a' * 40
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='v1.0.0', commit=fake_commit) == -1
    
    error = capsys.readouterr().err
    assert 'does not exist' in error or 'Cannot resolve' in error


def test_delete_tag(repo_with_commits: tuple[Repository, list[str]], 
                   capsys: CaptureFixture[str]) -> None:
    """Test deleting a tag via CLI."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    # Create a tag first
    repo.create_tag('v1.0.0')
    
    # Delete it via CLI
    assert cli_commands.delete_tag(working_dir_path=repo.working_dir,
                                   tag_name='v1.0.0') == 0
    
    assert 'Tag "v1.0.0" deleted' in capsys.readouterr().out
    
    # Verify tag is gone
    tag_path = repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / 'v1.0.0'
    assert not tag_path.exists()


def test_delete_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    """Test deleting a tag when no repository exists."""
    from caf import cli_commands
    
    assert cli_commands.delete_tag(working_dir_path=temp_repo_dir,
                                   tag_name='v1.0.0') == -1
    
    assert 'No repository found' in capsys.readouterr().err


def test_delete_tag_empty_name(repo_with_commits: tuple[Repository, list[str]], 
                               capsys: CaptureFixture[str]) -> None:
    """Test deleting a tag with an empty name."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    assert cli_commands.delete_tag(working_dir_path=repo.working_dir,
                                   tag_name='') == -1
    
    assert 'Tag name is required' in capsys.readouterr().err


def test_delete_nonexistent_tag(repo_with_commits: tuple[Repository, list[str]], 
                                capsys: CaptureFixture[str]) -> None:
    """Test deleting a tag that doesn't exist."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    assert cli_commands.delete_tag(working_dir_path=repo.working_dir,
                                   tag_name='nonexistent') == -1
    
    assert 'does not exist' in capsys.readouterr().err


def test_tags_command_empty(repo_with_commits: tuple[Repository, list[str]], 
                            capsys: CaptureFixture[str]) -> None:
    """Test listing tags when there are none."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    assert cli_commands.tags(working_dir_path=repo.working_dir) == 0
    
    assert 'No tags found' in capsys.readouterr().out


def test_tags_command_single(repo_with_commits: tuple[Repository, list[str]], 
                             capsys: CaptureFixture[str]) -> None:
    """Test listing a single tag."""
    from caf import cli_commands
    
    repo, commits = repo_with_commits
    
    repo.create_tag('v1.0.0', commits[1])
    
    assert cli_commands.tags(working_dir_path=repo.working_dir) == 0
    
    output = capsys.readouterr().out
    assert 'Tags:' in output
    assert 'v1.0.0' in output
    assert commits[1] in output


def test_tags_command_multiple(repo_with_commits: tuple[Repository, list[str]], 
                               capsys: CaptureFixture[str]) -> None:
    """Test listing multiple tags."""
    from caf import cli_commands
    
    repo, commits = repo_with_commits
    
    repo.create_tag('v1.0.0', commits[1])
    repo.create_tag('v0.1.0', commits[0])
    repo.create_tag('latest', commits[1])
    
    assert cli_commands.tags(working_dir_path=repo.working_dir) == 0
    
    output = capsys.readouterr().out
    assert 'Tags:' in output
    assert 'v0.1.0' in output
    assert 'v1.0.0' in output
    assert 'latest' in output
    assert commits[0] in output
    assert commits[1] in output


def test_tags_command_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    """Test listing tags when no repository exists."""
    from caf import cli_commands
    
    assert cli_commands.tags(working_dir_path=temp_repo_dir) == -1
    
    assert 'No repository found' in capsys.readouterr().err


def test_tags_command_shows_commit_info(repo_with_commits: tuple[Repository, list[str]], 
                                        capsys: CaptureFixture[str]) -> None:
    """Test that the tags command shows commit hashes."""
    from caf import cli_commands
    
    repo, commits = repo_with_commits
    
    repo.create_tag('v1.0.0', commits[0])
    
    assert cli_commands.tags(working_dir_path=repo.working_dir) == 0
    
    output = capsys.readouterr().out
    # Should show the tag name and commit hash
    assert 'v1.0.0' in output
    assert commits[0] in output


def test_create_tag_in_empty_repo(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    """Test creating a tag in an empty repository with no commits."""
    from caf import cli_commands
    
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir,
                                   tag_name='v1.0.0', commit=None) == -1
    
    error = capsys.readouterr().err
    assert 'No commits' in error or 'cannot resolve' in error.lower()


def test_workflow_create_list_delete(repo_with_commits: tuple[Repository, list[str]], 
                                     capsys: CaptureFixture[str]) -> None:
    """Test a complete workflow of creating, listing, and deleting tags."""
    from caf import cli_commands
    
    repo, _ = repo_with_commits
    
    # Create multiple tags
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='v1.0.0', commit=None) == 0
    capsys.readouterr()
    
    assert cli_commands.create_tag(working_dir_path=repo.working_dir,
                                   tag_name='v0.1.0', commit=None) == 0
    capsys.readouterr()
    
    # List tags
    assert cli_commands.tags(working_dir_path=repo.working_dir) == 0
    output = capsys.readouterr().out
    assert 'v0.1.0' in output
    assert 'v1.0.0' in output
    
    # Delete one tag
    assert cli_commands.delete_tag(working_dir_path=repo.working_dir,
                                   tag_name='v0.1.0') == 0
    capsys.readouterr()
    
    # List again - should only show v1.0.0
    assert cli_commands.tags(working_dir_path=repo.working_dir) == 0
    output = capsys.readouterr().out
    assert 'v0.1.0' not in output
    assert 'v1.0.0' in output