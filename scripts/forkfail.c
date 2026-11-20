/* Fail the first FORK_FAIL_BUDGET fork() calls with EAGAIN, then allow them.
 * Simulates the pids-cgroup exhaustion that made the Vulkan generator drop
 * shaders on a loaded CI runner, without touching the machine's real limits.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>

static long budget;
static pthread_mutex_t guard = PTHREAD_MUTEX_INITIALIZER;

__attribute__((constructor)) static void read_budget(void) {
    const char *value = getenv("FORK_FAIL_BUDGET");
    if (value != NULL) budget = strtol(value, NULL, 10);
}

pid_t fork(void) {
    static pid_t (*real_fork)(void);
    if (real_fork == NULL) real_fork = (pid_t (*)(void))dlsym(RTLD_NEXT, "fork");
    pthread_mutex_lock(&guard);
    int allow = budget <= 0;
    if (budget > 0) budget--;
    pthread_mutex_unlock(&guard);
    if (!allow) {
        errno = EAGAIN;
        return -1;
    }
    return real_fork();
}