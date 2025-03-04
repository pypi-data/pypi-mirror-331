import click
import json
import os

TODO_FILE = 'todo.json'

def load_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, 'r') as file:
        return json.load(file)
    
def save_tasks(tasks):
    with open(TODO_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)   

@click.group()
def cli():
    """Simple todo application"""
    pass

@cli.command()
@click.argument('task')
def add(task):
    """Add a new task"""
    tasks = load_tasks()
    tasks.append({'task': task, 'done': False})
    save_tasks(tasks)
    click.echo(f"Task '{task}' added successfully")

@cli.command(name='list')
def list():
    """List all tasks"""
    tasks = load_tasks()
    if not tasks:
        click.echo('No tasks found')
        return
    for i, task in enumerate(tasks, 1):
        status = '✅' if task['done'] else '❌'
        click.echo(f"{i}. {task['task']} - {status}")

@cli.command()
@click.argument('task_number', type=int)
def done(task_number):
    """Mark a task as done"""
    tasks = load_tasks()
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]['done'] = True
        save_tasks(tasks)
        click.echo(f"Task {task_number} marked as done")
    else:
        click.echo(f"`{task_number}` is not a valid task number")

@cli.command()
@click.argument('task_number', type=int)
def remove(task_number):
    """Remove a task"""
    tasks = load_tasks()
    if 0 < task_number <= len(tasks):
        deleted_task = tasks.pop(task_number - 1)
        save_tasks(tasks)
        click.echo(f"Task {task_number} removed successfully")
    else:
        click.echo(f"`{task_number}` is not a valid task number")

cli.add_command(done)
cli.add_command(add)
cli.add_command(list)
cli.add_command(remove)

if __name__ == '__main__':
    cli()
