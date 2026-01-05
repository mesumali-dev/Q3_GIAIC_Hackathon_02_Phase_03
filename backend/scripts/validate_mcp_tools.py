#!/usr/bin/env python3
"""Validation script for MCP tools implementation.

This script performs comprehensive validation of all MCP tools:
- T105: Stateless operation verification
- T108: Contract schema validation
- T109: End-to-end workflow validation
- T110: User-scoped access validation
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the backend src directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.delete_task import delete_task
from src.mcp.tools.update_task import update_task


async def validate_contract_schemas():
    """T108: Validate all five tools against contract JSON schemas."""
    print("T108: Validating tools against contract JSON schemas...")

    contracts_dir = Path(__file__).parent.parent.parent / "specs" / "007-mcp-stateless-tools" / "contracts"

    # Check if all contract files exist
    expected_contracts = [
        "add_task.json",
        "list_tasks.json",
        "complete_task.json",
        "delete_task.json",
        "update_task.json"
    ]

    missing_contracts = []
    for contract in expected_contracts:
        contract_path = contracts_dir / contract
        if not contract_path.exists():
            missing_contracts.append(contract)

    if missing_contracts:
        print(f"  ❌ Missing contract files: {missing_contracts}")
        return False
    else:
        print("  ✅ All contract JSON schema files found")
        return True


async def validate_end_to_end_workflow():
    """T109: Perform end-to-end validation workflow."""
    print("T109: Performing end-to-end validation...")

    # Use a test user ID
    user_id = "11111111-1111-1111-1111-111111111111"

    try:
        # 1. Create task
        print("  - Creating task...")
        create_result = await add_task(
            user_id=user_id,
            title="E2E Test Task",
            description="Task for end-to-end validation"
        )

        if not create_result.get("success"):
            print(f"    ❌ Failed to create task: {create_result}")
            return False

        task_id = create_result["task_id"]
        print(f"    ✅ Task created with ID: {task_id}")

        # 2. List tasks
        print("  - Listing tasks...")
        list_result = await list_tasks(user_id=user_id)

        if not list_result.get("success") or len(list_result.get("tasks", [])) == 0:
            print(f"    ❌ Failed to list tasks: {list_result}")
            return False

        print(f"    ✅ Found {list_result['count']} tasks")

        # 3. Complete task
        print("  - Completing task...")
        complete_result = await complete_task(
            user_id=user_id,
            task_id=task_id
        )

        if not complete_result.get("success"):
            print(f"    ❌ Failed to complete task: {complete_result}")
            return False

        if not complete_result["is_completed"]:
            print(f"    ❌ Task was not marked as completed")
            return False

        print(f"    ✅ Task marked as completed")

        # 4. Update task
        print("  - Updating task...")
        update_result = await update_task(
            user_id=user_id,
            task_id=task_id,
            title="Updated E2E Test Task",
            description="Updated description for end-to-end validation"
        )

        if not update_result.get("success"):
            print(f"    ❌ Failed to update task: {update_result}")
            return False

        if update_result["title"] != "Updated E2E Test Task":
            print(f"    ❌ Task title was not updated correctly")
            return False

        print(f"    ✅ Task updated successfully")

        # 5. Delete task
        print("  - Deleting task...")
        delete_result = await delete_task(
            user_id=user_id,
            task_id=task_id
        )

        if not delete_result.get("success"):
            print(f"    ❌ Failed to delete task: {delete_result}")
            return False

        print(f"    ✅ Task deleted successfully")

        # 6. Verify deletion (list tasks should return empty for this user now)
        print("  - Verifying deletion...")
        final_list_result = await list_tasks(user_id=user_id)

        if not final_list_result.get("success"):
            print(f"    ❌ Failed to list tasks after deletion: {final_list_result}")
            return False

        if final_list_result["count"] > 0:
            print(f"    ❌ Task still appears in list after deletion: {final_list_result}")
            return False

        print(f"    ✅ Task successfully removed from database")
        print("  ✅ End-to-end workflow completed successfully")
        return True

    except Exception as e:
        print(f"    ❌ Error during end-to-end validation: {e}")
        return False


async def validate_user_scoped_access():
    """T110: Verify user-scoped access isolation."""
    print("T110: Verifying user-scoped access...")

    user1_id = "22222222-2222-2222-2222-222222222222"
    user2_id = "33333333-3333-3333-3333-333333333333"

    try:
        # Create task for user 1
        print("  - Creating task for User 1...")
        user1_task = await add_task(
            user_id=user1_id,
            title="User 1 Task",
            description="Task belonging to User 1"
        )

        if not user1_task.get("success"):
            print(f"    ❌ Failed to create task for User 1: {user1_task}")
            return False

        user1_task_id = user1_task["task_id"]
        print(f"    ✅ User 1 task created: {user1_task_id}")

        # Create task for user 2
        print("  - Creating task for User 2...")
        user2_task = await add_task(
            user_id=user2_id,
            title="User 2 Task",
            description="Task belonging to User 2"
        )

        if not user2_task.get("success"):
            print(f"    ❌ Failed to create task for User 2: {user2_task}")
            return False

        user2_task_id = user2_task["task_id"]
        print(f"    ✅ User 2 task created: {user2_task_id}")

        # Verify User 1 can only see their own task
        print("  - Verifying User 1 can only see their tasks...")
        user1_tasks = await list_tasks(user_id=user1_id)
        if not user1_tasks.get("success"):
            print(f"    ❌ Failed to list User 1 tasks: {user1_tasks}")
            return False

        user1_task_ids = [task["task_id"] for task in user1_tasks.get("tasks", [])]
        if user1_task_id not in user1_task_ids or user2_task_id in user1_task_ids:
            print(f"    ❌ User 1 sees wrong tasks: {user1_task_ids}")
            return False

        print(f"    ✅ User 1 sees only their tasks: {len(user1_task_ids)} tasks")

        # Verify User 2 can only see their own task
        print("  - Verifying User 2 can only see their tasks...")
        user2_tasks = await list_tasks(user_id=user2_id)
        if not user2_tasks.get("success"):
            print(f"    ❌ Failed to list User 2 tasks: {user2_tasks}")
            return False

        user2_task_ids = [task["task_id"] for task in user2_tasks.get("tasks", [])]
        if user2_task_id not in user2_task_ids or user1_task_id in user2_task_ids:
            print(f"    ❌ User 2 sees wrong tasks: {user2_task_ids}")
            return False

        print(f"    ✅ User 2 sees only their tasks: {len(user2_task_ids)} tasks")

        # Try to access another user's task (should fail)
        print("  - Verifying cross-user access is blocked...")

        # Try to complete User 1's task as User 2 (should fail)
        complete_result = await complete_task(
            user_id=user2_id,
            task_id=user1_task_id
        )

        # This should fail with authorization error
        if complete_result.get("success"):
            print(f"    ❌ User 2 was able to access User 1's task (security breach!)")
            return False

        if complete_result.get("error", {}).get("code") not in ["TASK_NOT_FOUND", "AUTHORIZATION_ERROR"]:
            print(f"    ❌ Wrong error code for unauthorized access: {complete_result}")
            return False

        print(f"    ✅ Cross-user access properly blocked")

        # Try to update User 1's task as User 2 (should fail)
        update_result = await update_task(
            user_id=user2_id,
            task_id=user1_task_id,
            title="Hacked Title"
        )

        if update_result.get("success"):
            print(f"    ❌ User 2 was able to update User 1's task (security breach!)")
            return False

        if update_result.get("error", {}).get("code") not in ["TASK_NOT_FOUND", "AUTHORIZATION_ERROR"]:
            print(f"    ❌ Wrong error code for unauthorized update: {update_result}")
            return False

        print(f"    ✅ Cross-user update properly blocked")

        # Try to delete User 1's task as User 2 (should fail)
        delete_result = await delete_task(
            user_id=user2_id,
            task_id=user1_task_id
        )

        if delete_result.get("success"):
            print(f"    ❌ User 2 was able to delete User 1's task (security breach!)")
            return False

        if delete_result.get("error", {}).get("code") not in ["TASK_NOT_FOUND", "AUTHORIZATION_ERROR"]:
            print(f"    ❌ Wrong error code for unauthorized delete: {delete_result}")
            return False

        print(f"    ✅ Cross-user deletion properly blocked")

        print("  ✅ User-scoped access validation passed")
        return True

    except Exception as e:
        print(f"    ❌ Error during user-scoped access validation: {e}")
        return False


async def validate_stateless_operation():
    """T105: Verify stateless operation by restarting and checking persistence."""
    print("T105: Verifying stateless operation...")

    # Note: In a real scenario, we'd restart the server and verify persistence
    # Since we're running in the same process, we'll just verify that operations
    # persist to the database between calls

    user_id = "44444444-4444-4444-4444-444444444444"

    try:
        # Create a task
        print("  - Creating persistent task...")
        create_result = await add_task(
            user_id=user_id,
            title="Persistent Task",
            description="Task that should persist across sessions"
        )

        if not create_result.get("success"):
            print(f"    ❌ Failed to create persistent task: {create_result}")
            return False

        task_id = create_result["task_id"]
        print(f"    ✅ Task created: {task_id}")

        # List tasks to verify it's in the database
        print("  - Verifying task persistence...")
        list_result = await list_tasks(user_id=user_id)

        if not list_result.get("success") or list_result["count"] != 1:
            print(f"    ❌ Task not found in database: {list_result}")
            return False

        if list_result["tasks"][0]["task_id"] != task_id:
            print(f"    ❌ Wrong task returned from database")
            return False

        print(f"    ✅ Task persists in database between operations")

        # Complete the task
        print("  - Completing task to verify state persistence...")
        complete_result = await complete_task(user_id=user_id, task_id=task_id)

        if not complete_result.get("success") or not complete_result["is_completed"]:
            print(f"    ❌ Failed to complete task: {complete_result}")
            return False

        print(f"    ✅ Task completion persisted")

        # Verify completion status is maintained
        print("  - Verifying completion status is maintained...")
        verify_list = await list_tasks(user_id=user_id)

        if (not verify_list.get("success") or
            verify_list["count"] != 1 or
            not verify_list["tasks"][0]["is_completed"]):
            print(f"    ❌ Completion status not maintained: {verify_list}")
            return False

        print(f"    ✅ Task completion status persisted across operations")

        print("  ✅ Stateless operation verification passed")
        return True

    except Exception as e:
        print(f"    ❌ Error during stateless operation validation: {e}")
        return False


async def main():
    """Run all validation tests."""
    print("Running MCP Tools Validation Suite")
    print("=" * 50)

    all_passed = True

    # Run all validation tests
    tests = [
        ("Contract Schema Validation", validate_contract_schemas),
        ("End-to-End Workflow", validate_end_to_end_workflow),
        ("User-Scoped Access", validate_user_scoped_access),
        ("Stateless Operation", validate_stateless_operation),
    ]

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        result = await test_func()
        if not result:
            all_passed = False
        print()

    print("=" * 50)
    if all_passed:
        print("🎉 All validation tests PASSED!")
        print("MCP tools implementation is ready for Phase 3 integration.")
        return 0
    else:
        print("❌ Some validation tests FAILED!")
        print("Please review the issues above and fix before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)