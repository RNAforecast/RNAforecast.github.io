Training
########

:title: Training, RNA Forecast | ViennaRNA and local AI tools
:slug: training
:description: Hands-on training for research groups in ViennaRNA and RNA design, and in local AI coding tools. Both in preparation, both with a waitlist.
:referrer: no-referrer-when-downgrade
:summary: Two hands-on training formats for research groups, remote or on site, one on ViennaRNA and computational RNA design and one on local AI coding tools. Both are in preparation and both have a waitlist.
:og_type: website
:hero_kicker: Training
:hero_title: Hands-on training for research groups
:hero_lead: RNA Forecast is preparing two hands-on formats for research groups, remote or on site. There are no dates yet. Whoever joins one of the waitlists gets one message from RNA Forecast, when the first date is fixed.
:hero_actions: `Join the ViennaRNA waitlist <#viennarna-waitlist>`__ `Join the local AI waitlist <#waitlist>`__

.. container:: lead

  Michael T. Wolfinger has taught computational RNA biology since 2005, in
  university courses at the University of Vienna, the University of Freiburg
  and FH Campus Wien, and in invited workshops for research teams. The formats
  below grow out of that teaching. They are practical: participants work on
  real sequences and leave with workflows they can run again. Content and
  pacing are adjusted to the group before the session.

.. _viennarna:

ViennaRNA and computational RNA design
--------------------------------------

.. container:: kicker

  In preparation

.. container:: split

  .. container:: split-main

    This material has been taught in university courses and small groups. As
    an RNA Forecast training it is being prepared, and dates will be announced
    to the waitlist first.

    **Who it is for.** Experimental RNA labs that want computational depth,
    doctoral programmes, biotech teams working on mRNA, siRNA or structured
    RNA, computational groups and tool developers.

    **What is covered**, chosen per group, half day to full day:

    - RNA secondary structure and the nearest neighbour model: what ``RNAfold``
      computes, and why the MFE structure is one answer among many.
    - The Boltzmann ensemble, i.e. pair probabilities, centroid and MEA
      structures, ensemble diversity and helix probabilities, how to read a dot
      plot, and when the MFE misleads.
    - Probing data, i.e. SHAPE and DMS reactivities as soft constraints, the
      three ViennaRNA methods and, new in ViennaRNA 2.8.0, cross-linking
      interval pairs, with a look at what the data change and what they do not.
    - Modified nucleotides, i.e. the pseudouridine and N1-methylpseudouridine
      parameters for therapeutic mRNA, so that the molecule that is folded is
      the one that is made.
    - Large RNAs and viral genomes: local folding with ``RNAplfold``, locally
      stable elements, conserved structure from alignments with ``RNAalifold``,
      covariation as evidence.
    - Accessibility and RNA–RNA interaction: ``RNAplfold``, ``RNAcofold`` and
      ``RNAup`` for siRNA, ASO and miRNA sites, and how to map variants onto a
      structure.
    - `RNA structure review </structure-review/>`__ before synthesis, i.e. the objective, the ensemble
      defect and how a design holds up under sequence variants, with a
      checklist that participants take home.

    Tertiary structure prediction is outside the scope. The course covers how
    far secondary structure and ensembles take a question before that becomes
    necessary.

    **Format.** Live, remote or on site, as a group of 6 to 12 or as a single
    participant in an open remote cohort, half day or full day, participants'
    own sequences welcome. Materials stay with the group.

    Free material on the topic, in reading order on the
    `ViennaRNA in practice <https://michaelwolfinger.com/rna-structure-prediction/>`__
    page:
    `RNAfold and the ensemble <https://michaelwolfinger.com/blog/2026/rnafold-in-practice/>`__,
    `SHAPE and chemical probing data <https://michaelwolfinger.com/blog/2026/How-to-Interpret-SHAPE-and-Chemical-Probing-Data-for-RNA-Structure-Decisions/>`__,
    `RNAplfold and accessibility <https://michaelwolfinger.com/blog/2026/rnaplfold-accessibility/>`__,
    the `ViennaRNA 2.8.0 release note <https://michaelwolfinger.com/blog/2026/viennarna-2-8-0/>`__
    and the `RNA structure glossary <https://michaelwolfinger.com/glossary/>`__.

  .. container:: blueprint

    .. container:: kicker-sm

      Waitlist

    .. raw:: html

      <form class="contact-form" method="post" id="viennarna-waitlist"
            action="https://forms.rnaforecast.com/rnaf-waitlist-viennarna">
        <p class="form-error" id="viennarna-error">Something was missing or not valid. Please check the fields and send again.</p>
        <input type="hidden" name="topic" value="viennarna" />
        <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" />
        <p class="field">
          <label for="viennarna-name">Name</label>
          <input class="input" type="text" id="viennarna-name" name="name"
                 autocomplete="name" />
        </p>
        <p class="field">
          <label for="viennarna-email">Email <abbr title="required">*</abbr></label>
          <input class="input" type="email" id="viennarna-email" name="email"
                 autocomplete="email" required />
        </p>
        <p class="field">
          <label for="viennarna-organization">Affiliation</label>
          <input class="input" type="text" id="viennarna-organization" name="organization"
                 autocomplete="organization" placeholder="Institute, company or group" />
        </p>
        <p class="field">
          <label for="viennarna-role">You are</label>
          <select class="input" id="viennarna-role" name="role">
            <option value="">Choose one</option>
            <option value="experimental-lab">An experimental lab</option>
            <option value="computational-group">A computational group</option>
            <option value="biotech-industry">Biotech or industry</option>
            <option value="doctoral-programme">A doctoral programme or course</option>
            <option value="tool-developer">A tool developer</option>
            <option value="other">Something else</option>
          </select>
        </p>
        <p class="field">
          <label for="viennarna-format">Preferred format</label>
          <select class="input" id="viennarna-format" name="format">
            <option value="">No preference yet</option>
            <option value="remote">Remote</option>
            <option value="on-site">On site</option>
            <option value="either">Either</option>
          </select>
        </p>
        <p class="field">
          <label for="viennarna-group">Who would attend</label>
          <select class="input" id="viennarna-group" name="group">
            <option value="">Not sure yet</option>
            <option value="just-me">Just me</option>
            <option value="2-5">2 to 5 people</option>
            <option value="6-12">6 to 12 people</option>
            <option value="more-than-12">More than 12</option>
          </select>
        </p>
        <p class="field">
          <label for="viennarna-wish">What should it cover?</label>
          <textarea class="input" id="viennarna-wish" name="wishes" rows="3"
                    placeholder="Your sequences, your questions, the methods you want to see"></textarea>
        </p>
        <p class="form-note">You get one e-mail when a date is fixed and nothing else, and a reply to that e-mail takes you off the list.</p>
        <button class="btn btn-primary btn-block" type="submit">Join the ViennaRNA waitlist</button>
        <p class="form-note form-fallback">Problems with the form? Email
          <a href="mailto:hello@rnaforecast.com">hello&#64;rnaforecast.com</a>.</p>
      </form>

.. _local-ai-tools:

Local AI coding tools for research groups and small teams
---------------------------------------------------------

.. container:: kicker

  In preparation

.. container:: split

  .. container:: split-main

    The setup guides this course is built on are published and maintained on
    michaelwolfinger.com. The course itself is in preparation and will run as
    a live half-day cohort, updated for every run because the tools change
    monthly.

    A scientist's workshop on running coding agents, Claude Code, OpenAI
    Codex CLI, OpenCode and pi, against models that run on your own hardware
    with LM Studio, Ollama or an exo cluster across several machines, on Apple
    Silicon and on Linux with NVIDIA or AMD GPUs, with notes for Windows. For
    research groups and small teams whose data must stay in house: unpublished
    data, manuscripts and code that must not leave the machine.

    **What is covered:**

    - Hardware and model choice, i.e. what fits in 16, 24, 32 and 64+ GB with
      measured memory needs, tool calling as the property that decides whether
      a model is usable at all (and how to check it instead of trusting the
      agent's report), and context size as the second limit.
    - Setup on macOS and Linux, with the differences on Windows, i.e. LM Studio,
      Ollama, the environment variables and the context length, which is the
      setting that breaks most sessions.
    - A research workflow: scripts and analysis notebooks, tests as the safety
      net, ``AGENTS.md`` and ``CLAUDE.md`` for durable instructions, reading
      diffs.
    - What local models can and cannot do compared with hosted ones, where
      they fail, and how to work around it.
    - Privacy and cost: what leaves the machine with each configuration,
      telemetry switches, what a GPU box costs against API spend.
    - Hands-on: every participant leaves with a working setup on their laptop
      or against the group's server.

    **Prerequisites.** A laptop with 16 GB or more, or access to a group
    machine, and some comfort with a terminal. **Format.** Live cohort, half day, 6 to
    12 participants, remote or on site.

    The guides:
    `Claude Code with a local model on Apple Silicon <https://michaelwolfinger.com/blog/2026/claude-code-local-llm-apple-silicon/>`__,
    `Claude Code with Ollama <https://michaelwolfinger.com/blog/2026/claude-code-ollama-local-llm/>`__,
    `Codex CLI with LM Studio, Ollama or exo <https://michaelwolfinger.com/blog/2026/codex-cli-local-model-lm-studio-ollama/>`__,
    `four coding agents against ten local models <https://michaelwolfinger.com/blog/2026/coding-agents-local-models-exo-cluster/>`__
    and `a reproducible data analysis with a local model <https://michaelwolfinger.com/blog/2026/claude-code-scientific-data-analysis/>`__.

  .. container:: blueprint

    .. container:: kicker-sm

      Waitlist

    .. raw:: html

      <form class="contact-form" method="post" id="waitlist"
            action="https://forms.rnaforecast.com/rnaf-waitlist-local-ai-tools">
        <p class="form-error" id="local-ai-tools-error">Something was missing or not valid. Please check the fields and send again.</p>
        <input type="hidden" name="topic" value="local-ai-tools" />
        <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" />
        <p class="field">
          <label for="local-ai-tools-name">Name</label>
          <input class="input" type="text" id="local-ai-tools-name" name="name"
                 autocomplete="name" />
        </p>
        <p class="field">
          <label for="local-ai-tools-email">Email <abbr title="required">*</abbr></label>
          <input class="input" type="email" id="local-ai-tools-email" name="email"
                 autocomplete="email" required />
        </p>
        <p class="field">
          <label for="local-ai-tools-organization">Affiliation</label>
          <input class="input" type="text" id="local-ai-tools-organization" name="organization"
                 autocomplete="organization" placeholder="Institute, company or group" />
        </p>
        <p class="field">
          <label for="local-ai-tools-role">You are</label>
          <select class="input" id="local-ai-tools-role" name="role">
            <option value="">Choose one</option>
            <option value="experimental-lab">An experimental lab</option>
            <option value="computational-group">A computational group</option>
            <option value="biotech-industry">Biotech or industry</option>
            <option value="doctoral-programme">A doctoral programme or course</option>
            <option value="tool-developer">A tool developer</option>
            <option value="other">Something else</option>
          </select>
        </p>
        <p class="field">
          <label for="local-ai-tools-format">Preferred format</label>
          <select class="input" id="local-ai-tools-format" name="format">
            <option value="">No preference yet</option>
            <option value="remote">Remote</option>
            <option value="on-site">On site</option>
            <option value="either">Either</option>
          </select>
        </p>
        <p class="field">
          <label for="local-ai-tools-group">Who would attend</label>
          <select class="input" id="local-ai-tools-group" name="group">
            <option value="">Not sure yet</option>
            <option value="just-me">Just me</option>
            <option value="2-5">2 to 5 people</option>
            <option value="6-12">6 to 12 people</option>
            <option value="more-than-12">More than 12</option>
          </select>
        </p>
        <p class="field">
          <label for="local-ai-tools-wish">What should it cover?</label>
          <textarea class="input" id="local-ai-tools-wish" name="wishes" rows="3"
                    placeholder="Your hardware, your workflow, what must stay on the machine"></textarea>
        </p>
        <p class="form-note">You get one e-mail when a date is fixed and nothing else, and a reply to that e-mail takes you off the list.</p>
        <button class="btn btn-primary btn-block" type="submit">Join the local AI tools waitlist</button>
        <p class="form-note form-fallback">Problems with the form? Email
          <a href="mailto:hello@rnaforecast.com">hello&#64;rnaforecast.com</a>.</p>
      </form>

.. container:: closing

  Questions about either format, or a group with a specific need:
  `hello@rnaforecast.com <mailto:hello@rnaforecast.com>`__
  or the `contact form </#contact>`__.
