from datetime import timedelta
import asyncio
import rio
import extensions.rio_jobs as rio_jobs


# Regular code to create your Rio app
class MyRoot(rio.Component):
    def build(self) -> rio.Component:
        return rio.Text(
            "Hello, world!",
            justify="center",
        )


# Create a function for the scheduler to run. This function can by synchronous
# or asynchronous.
async def my_job() -> timedelta:
    # Do some work here
    print("Working hard!")
    await asyncio.sleep(100)

    # Optionally reschedule the job. This can return
    #
    # - `None` to keep running the the configured interval
    # - a `datetime` object to schedule the job at a specific time
    # - a `timedelta` object to schedule the job at a relative time
    # - literal `never` to stop the job
    #
    # ...
    return timedelta(hours=3)


# Create a scheduler and schedule the job
scheduler = rio_jobs.JobScheduler()

scheduler.schedule(
    my_job,
    interval=timedelta(hours=1),
)


# Pass the scheduler to the Rio app. Since Rio's extension interface isn't
# stable yet, we'll add the extension manually after the app has been created.
app = rio.App(
    build=MyRoot,
    # ...
)

app._add_extension(scheduler)


# Run your Rio app as usual. If you want to use `rio run`, remove this line
app.run_in_browser()
