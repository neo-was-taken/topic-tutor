# Scenario 05: non-code topic

Topic: debugging Kubernetes networking with kubectl. Recorded 2026-11-17 against
`dist/learn-topic-prompt.md`. The tutor session was given the topic only: no workspace
path, no scenario script, no pass criteria. Learner lines are the fixed script from
`tests/scenarios/README.md`, relayed verbatim. Run to the first lesson's TEACH step.

Verified on disk after the run, not taken from the tutor's claims:

- `/tmp/learn-topic/05-non-code/` holds the three files, written only after the workspace
  question was answered.
- All 24 lessons in `CURRICULUM.md` carry goal, concept and done when; every done when
  names a command or an observation on the cluster.
- Five lessons inject a fault and have the learner observe the failure: `L1.4` selector,
  `L1.6` readiness probe, `L3.4` CoreDNS scaled to zero, `L4.2` ingress policy, `L4.3`
  egress policy blocking DNS.
- `TOPIC.md` out of scope names service meshes, Ingress and L7, LoadBalancer and cloud
  integration, multi-cluster, CNI internals and IPv6.
- `TOPIC.md` pins nothing: kind, Kubernetes and CNI versions are recorded as unknown until
  read off the cluster.
- No project scaffolding, no repository and no build step anywhere in the course. The only
  artifacts are throwaway manifests and the learner's own checklist in `L5.1`.

## LEARNER

I want to learn how to debug Kubernetes networking with kubectl. This is a new course, nothing exists yet.

## TUTOR

Good topic to learn by doing, since networking bugs only make sense when you can see them fail.

First question of three:

What do you want to be able to do at the end, and what would prove it? For example: "given a report that service X can't reach service Y, find the cause in under 10 minutes" — proof being that you diagnose a broken setup I hand you, unaided, and name the exact layer that is wrong (DNS, Service selector, endpoints, NetworkPolicy, ingress).

Tell me your version of that, in your own words.

## LEARNER

when a pod cannot reach a service, find out why myself instead of asking the platform team. Proof would be: given a broken cluster, I find the cause unaided.

## TUTOR

Clear. That is a diagnosis goal, not a configuration goal, so the course will be about reading cluster state rather than writing manifests.

Second question of three:

What do you already know here? Specifically:

- kubectl: which commands do you use today without looking them up?
- Kubernetes objects: are Service, Endpoints/EndpointSlice, and NetworkPolicy familiar names, vague names, or new?
- Networking basics: are you comfortable with DNS resolution, TCP ports, and curl?

Rough answers are fine.

## LEARNER

I write services and know Docker well. I use kubectl get and kubectl logs and nothing else. I have never read a Service or an Endpoints object. DNS, ports and curl are fine.

## TUTOR

Useful. So the gap is Kubernetes objects, not networking itself. You read TCP and DNS fine; you just cannot yet see what the cluster thinks it is doing.

Third question of three:

Where will you type things, and how do we check the result?

- Do you have a cluster you can break safely, and which kind? (kind, minikube, k3d, Docker Desktop, a real dev cluster)
- Do you have cluster-admin on it, or are you limited to one namespace?
- Is a CNI with NetworkPolicy enforcement available? Plain kind, for example, installs kindnet, which ignores NetworkPolicy, so policies appear to work but block nothing.

If you are not sure about the last one, say so and we will check it with a command in lesson 1 instead of guessing.

## LEARNER

a local kind cluster I can break and recreate, kubectl in a terminal, I paste the output. I have cluster-admin on it. Not sure about the CNI, it is whatever kind gives me by default.

## TUTOR

That answers everything I need about the topic. Default kind gives you kindnet, which accepts NetworkPolicy objects and enforces nothing, so I will put a lesson early that verifies this on your cluster and switches kind to Calico if needed, before any policy lesson claims to prove something.

Last question before I write anything:

Where should the three course files go? I will create `TOPIC.md`, `CURRICULUM.md` and `PROGRESS.md`. The working directory here is `/home/whatever/Documents/projects/topic-tutor`, so a subfolder like `/home/whatever/Documents/projects/topic-tutor/courses/k8s-net-debug/` would keep them together, but name any path you prefer.

## LEARNER

/tmp/learn-topic/05-non-code

## TUTOR

Written to `/tmp/learn-topic/05-non-code/`: `TOPIC.md`, `CURRICULUM.md`, `PROGRESS.md`.

Assumptions I filled in, correct me on any: 20-30 minutes per session, one lesson per sitting; pace 3; no version pins yet, since a version I guess is not a pin, so L0.1 reads kind, Kubernetes and CNI off your cluster. Out of scope: Ingress and L7, service meshes, LoadBalancer and cloud integration, CNI internals, writing production manifests. I inject faults, you diagnose them; I never explain a fault before you find it.

24 lessons, 6 phases:

Phase 0 - A cluster you can trust
- L0.1 Rebuild the cluster from a config file
- L0.2 Find out whether NetworkPolicy is enforced
- L0.3 Stand up the practice app

Phase 1 - Reading what the cluster thinks
- L1.1 Read a Service object field by field
- L1.2 Labels and selectors
- L1.3 EndpointSlice: the cluster's answer
- L1.4 Fault: the selector that matches nothing
- L1.5 Fault: targetPort pointing at the wrong port
- L1.6 Readiness probes silently empty your endpoints

Phase 2 - Testing from inside the cluster
- L2.1 Get a shell and curl where you need one
- L2.2 Narrow the layer: pod IP, then ClusterIP, then name
- L2.3 What port-forward does and does not prove
- L2.4 Read the symptom: timeout vs refused vs NXDOMAIN

Phase 3 - DNS
- L3.1 Service DNS names and the search domain
- L3.2 Resolve a Service from a pod
- L3.3 Headless Services resolve to pod IPs
- L3.4 Fault: CoreDNS is the problem

Phase 4 - NetworkPolicy
- L4.1 Default allow, and the policy that flips it
- L4.2 Fault: an ingress policy blocking the client
- L4.3 Fault: egress policy that blocks DNS
- L4.4 Which policies apply to this pod?

Phase 5 - Doing it unaided
- L5.1 Your own checklist, in order
- L5.2 Peek at kube-proxy and iptables (opt)
- L5.3 Final: an unknown fault, diagnosed unaided

What do you want cut or reordered before I freeze this?

## LEARNER

no service mesh, I will never run one

## TUTOR

Already covered. `TOPIC.md` out of scope line names service meshes, along with Ingress and L7 routing, LoadBalancer and cloud integration, multi-cluster, CNI internals and IPv6. No curriculum change needed, so nothing to amend.

That was a cut, not an approval. Do you approve the 24-lesson list as it stands, or is there anything else to cut or reorder?

## LEARNER

approved, start

## TUTOR

Curriculum frozen. Starting L0.1.

**L0.1 Rebuild the cluster from a config file — GOAL**

You will create the practice cluster from a saved kind config file, so you can throw away any cluster I break and get an identical one back in a minute. Afterwards you will also know the exact kind, Kubernetes and CNI versions you are working with, read off the cluster rather than assumed.

Ready to start, or any questions about the goal first?

## LEARNER

ready

## TUTOR

**L0.1 — TEACH**

Concept: a kind cluster is defined by a file, not by the commands you happened to type. Without the file, "recreate my cluster" means remembering flags. With it, recreation is one command and the result is identical every time. That matters here because I will break your cluster on purpose, and a rebuild must not change the thing we are measuring.

Save this as `kind-practice.yaml` in your workspace:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: netdebug
nodes:
  - role: control-plane
  - role: worker
```

Two nodes, because pod-to-pod traffic crossing a node boundary exercises the CNI, which a single-node cluster can hide.

I have deliberately not pinned a node image. Your local kind picks its own default Kubernetes version, and we will read that version off the cluster instead of me guessing a tag that may not exist for your kind build.

Check question before you run anything: `kubectl version` prints two versions, client and server. Which of those two does this config file influence, and which comes from the kubectl binary on your machine?
