from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import os
import re
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager


@dataclass
class GitContext:
    git_repos_path: str


@asynccontextmanager
async def git_lifespan(server: FastMCP) -> AsyncIterator[GitContext]:
    """Manage Git repositories lifecycle"""
    # read .env
    import dotenv

    dotenv.load_dotenv()
    git_repos_path = os.environ.get('GIT_REPOS_PATH', os.getcwd())

    try:
        yield GitContext(git_repos_path=git_repos_path)
    finally:
        pass  # No cleanup needed


mcp = FastMCP('git-mcp', lifespan=git_lifespan)


def _run_git_command(repo_path: str, command: List[str]) -> str:
    """Run a git command in the specified repository path"""
    if not os.path.exists(repo_path):
        raise ValueError(f'Repository path does not exist: {repo_path}')

    full_command = ['git'] + command
    try:
        result = subprocess.run(
            full_command,
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else str(e)
        raise ValueError(f'Git command failed: {error_message}')


@mcp.tool()
def get_last_git_tag(ctx: Context, repo_name: str) -> Dict[str, str]:
    """Find the last git tag in the repository

    Args:
        repo_name: Name of the git repository

    Returns:
        Dictionary containing tag version and date
    """
    git_repos_path = ctx.request_context.lifespan_context.git_repos_path
    repo_path = os.path.join(git_repos_path, repo_name)
    
    # Get the most recent tag
    try:
        # Get the most recent tag name
        tag_name = _run_git_command(repo_path, ['describe', '--tags', '--abbrev=0'])
        
        # Get the tag date
        tag_date_str = _run_git_command(
            repo_path, 
            ['log', '-1', '--format=%ai', tag_name]
        )
        
        # Parse the date string into a datetime object
        tag_date = datetime.strptime(tag_date_str, '%Y-%m-%d %H:%M:%S %z')
        formatted_date = tag_date.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'version': tag_name,
            'date': formatted_date
        }
    except ValueError as e:
        if 'No names found' in str(e):
            return {
                'version': 'No tags found',
                'date': ''
            }
        raise e


@mcp.tool()
def list_commits_since_last_tag(
    ctx: Context, repo_name: str, max_count: Optional[int] = None
) -> List[Dict[str, str]]:
    """List commit messages since main HEAD and the last git tag

    Args:
        repo_name: Name of the git repository
        max_count: Maximum number of commits to return

    Returns:
        List of dictionaries containing commit hash, author, date, and message
    """
    git_repos_path = ctx.request_context.lifespan_context.git_repos_path
    repo_path = os.path.join(git_repos_path, repo_name)
    
    try:
        # Try to get the most recent tag
        last_tag = _run_git_command(repo_path, ['describe', '--tags', '--abbrev=0'])
    except ValueError as e:
        if 'No names found' in str(e):
            # If no tags found, return all commits
            last_tag = ''
        else:
            raise e
    
    # Build the git log command
    log_command = ['log', '--pretty=format:%H|%an|%ad|%s', '--date=iso']
    
    if last_tag:
        log_command.append(f'{last_tag}..HEAD')
    
    if max_count is not None:
        log_command.extend(['-n', str(max_count)])
    
    # Get the commit logs
    commit_logs = _run_git_command(repo_path, log_command)
    
    # Parse the commit logs
    commits = []
    if commit_logs:
        for line in commit_logs.split('\n'):
            if not line.strip():
                continue
                
            parts = line.split('|', 3)
            if len(parts) == 4:
                commit_hash, author, date, message = parts
                commits.append({
                    'hash': commit_hash,
                    'author': author,
                    'date': date,
                    'message': message
                })
    
    return commits


@mcp.tool()
def list_repositories(ctx: Context) -> List[str]:
    """List all git repositories in the configured path

    Returns:
        List of repository names
    """
    git_repos_path = ctx.request_context.lifespan_context.git_repos_path
    
    if not os.path.exists(git_repos_path):
        raise ValueError(f'Git repositories path does not exist: {git_repos_path}')
    
    repos = []
    for item in os.listdir(git_repos_path):
        item_path = os.path.join(git_repos_path, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
            repos.append(item)
    
    return repos


@mcp.tool()
def create_git_tag(ctx: Context, repo_name: str, tag_name: str, message: Optional[str] = None) -> Dict[str, str]:
    """Create a new git tag in the repository

    Args:
        repo_name: Name of the git repository
        tag_name: Name of the tag to create
        message: Optional message for annotated tag

    Returns:
        Dictionary containing status and tag information
    """
    git_repos_path = ctx.request_context.lifespan_context.git_repos_path
    repo_path = os.path.join(git_repos_path, repo_name)
    
    # Validate repository exists
    if not os.path.exists(repo_path) or not os.path.exists(os.path.join(repo_path, '.git')):
        raise ValueError(f'Repository not found: {repo_name}')
    
    # Create the tag command
    if message:
        # Create annotated tag with message
        tag_command = ['tag', '-a', tag_name, '-m', message]
    else:
        # Create lightweight tag
        tag_command = ['tag', tag_name]
    
    # Execute the tag command
    try:
        _run_git_command(repo_path, tag_command)
        
        # Get tag date
        tag_date_str = _run_git_command(
            repo_path, 
            ['log', '-1', '--format=%ai', tag_name]
        )
        
        # Parse the date string into a datetime object
        tag_date = datetime.strptime(tag_date_str, '%Y-%m-%d %H:%M:%S %z')
        formatted_date = tag_date.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'status': 'success',
            'version': tag_name,
            'date': formatted_date,
            'type': 'annotated' if message else 'lightweight'
        }
    except ValueError as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@mcp.tool()
def push_git_tag(ctx: Context, repo_name: str, tag_name: str) -> Dict[str, str]:
    """Push a git tag to the default remote

    Args:
        repo_name: Name of the git repository
        tag_name: Name of the tag to push

    Returns:
        Dictionary containing status and information about the operation
    """
    git_repos_path = ctx.request_context.lifespan_context.git_repos_path
    repo_path = os.path.join(git_repos_path, repo_name)
    
    # Validate repository exists
    if not os.path.exists(repo_path) or not os.path.exists(os.path.join(repo_path, '.git')):
        raise ValueError(f'Repository not found: {repo_name}')
    
    # Validate tag exists
    try:
        _run_git_command(repo_path, ['tag', '-l', tag_name])
    except ValueError:
        return {
            'status': 'error',
            'error': f'Tag {tag_name} not found in repository {repo_name}'
        }
    
    # Get the default remote (usually 'origin')
    try:
        remote = _run_git_command(repo_path, ['remote'])
        if not remote:
            return {
                'status': 'error',
                'error': f'No remote configured for repository {repo_name}'
            }
        # Use the first remote if multiple are available
        default_remote = remote.split('\n')[0].strip()
        
        # Push the tag to the remote
        push_result = _run_git_command(repo_path, ['push', default_remote, tag_name])
        
        return {
            'status': 'success',
            'remote': default_remote,
            'tag': tag_name,
            'message': f'Successfully pushed tag {tag_name} to remote {default_remote}'
        }
    except ValueError as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@mcp.tool()
async def refresh_repository(ctx: Context, repo_name: str) -> Dict:
    '''Refresh repository by checking out main branch and pulling all remotes
    
    Args:
        repo_name: Name of the git repository
    
    Returns:
        Dictionary containing status and information about the operation
    '''
    git_ctx = ctx.get_context(GitContext)
    repo_path = os.path.join(git_ctx.git_repos_path, repo_name)
    
    # Validate repository exists
    if not os.path.exists(repo_path) or not os.path.exists(os.path.join(repo_path, '.git')):
        raise ValueError(f'Repository not found: {repo_name}')
    
    try:
        # Get all remotes
        remotes = _run_git_command(repo_path, ['remote']).strip().split('\n')
        if not remotes or remotes[0] == '':
            return {
                'status': 'error',
                'error': f'No remotes configured for repository {repo_name}'
            }
        
        # Checkout main branch
        try:
            _run_git_command(repo_path, ['checkout', 'main'])
        except ValueError as e:
            # Try master if main doesn't exist
            try:
                _run_git_command(repo_path, ['checkout', 'master'])
            except ValueError:
                return {
                    'status': 'error',
                    'error': f'Failed to checkout main or master branch: {str(e)}'
                }
        
        # Pull from all remotes
        pull_results = {}
        for remote in remotes:
            if remote:  # Skip empty remote names
                try:
                    result = _run_git_command(repo_path, ['pull', remote, 'main'])
                    pull_results[remote] = 'success'
                except ValueError as e:
                    # Try master if main doesn't exist
                    try:
                        result = _run_git_command(repo_path, ['pull', remote, 'master'])
                        pull_results[remote] = 'success'
                    except ValueError as e:
                        pull_results[remote] = f'error: {str(e)}'
        
        return {
            'status': 'success',
            'repository': repo_name,
            'branch': 'main',
            'pull_results': pull_results
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Failed to refresh repository: {str(e)}'
        }

from importlib.metadata import version
try:
    __version__ = version("git-mcp")
    print(f"Starting MCP server version {__version__}")
except Exception:
    print("Starting MCP server (version unknown)")
