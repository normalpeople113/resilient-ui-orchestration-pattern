def atomic_state_sync(external_store, task_id, new_status, metadata=None):
    """
    Pattern: Pre-lock → Execute → Post-update with rollback capability.
    """
    current = external_store.get(task_id)
    if current in ("COMPLETED", "PROCESSING"):
        return False  # Idempotent guard
        
    external_store.update(task_id, status="PROCESSING")
    try:
        # Execute business logic
        yield
        external_store.update(task_id, status=new_status, meta=metadata)
    except Exception as e:
        external_store.update(task_id, status="FAILED", error=str(e))
        raise
    finally:
        external_store.sync()  # Ensure atomic flush
