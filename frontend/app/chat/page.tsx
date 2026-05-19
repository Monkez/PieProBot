"use client";

import { apiAuthHeaders, apiPost, apiUrl } from "@/lib/api";
import { FileAudio, FileImage, FileText, Mic, Paperclip, Send, Square, Trash2, X } from "lucide-react";
import { useMemo, useRef, useState } from "react";

type Attachment = {
  id?: string;
  original_name: string;
  content_type: string;
  size: number;
  kind: "image" | "voice" | "file";
  path?: string;
};

type ChatResult = {
  task_id: string;
  status: string;
  response: string;
  attachments?: Attachment[];
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  status?: string;
  attachments?: AttachmentPreview[];
  taskId?: string;
};

type AttachmentPreview = {
  id: string;
  file: File;
  name: string;
  type: string;
  size: number;
  kind: "image" | "voice" | "file";
  url?: string;
};

function attachmentKind(file: File): "image" | "voice" | "file" {
  if (file.type.startsWith("image/")) return "image";
  if (file.type.startsWith("audio/")) return "voice";
  return "file";
}

function formatBytes(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function newId(prefix: string): string {
  return `${prefix}_${Math.random().toString(16).slice(2)}_${Date.now()}`;
}

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "system",
      content: "Chat Console is ready. Send text, images, files, or voice notes to create an agent task."
    }
  ]);
  const [attachments, setAttachments] = useState<AttachmentPreview[]>([]);
  const [busy, setBusy] = useState(false);
  const [recording, setRecording] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);

  const canSend = useMemo(() => message.trim().length > 0 || attachments.length > 0, [message, attachments]);

  function addFiles(files: FileList | File[]) {
    const next = Array.from(files).slice(0, Math.max(0, 8 - attachments.length)).map((file) => {
      const kind = attachmentKind(file);
      return {
        id: newId("att"),
        file,
        name: file.name,
        type: file.type || "application/octet-stream",
        size: file.size,
        kind,
        url: kind === "image" || kind === "voice" ? URL.createObjectURL(file) : undefined
      };
    });
    setAttachments((current) => [...current, ...next]);
  }

  function removeAttachment(id: string) {
    setAttachments((current) => {
      const item = current.find((entry) => entry.id === id);
      if (item?.url) URL.revokeObjectURL(item.url);
      return current.filter((entry) => entry.id !== id);
    });
  }

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setMessages((current) => [
        ...current,
        { id: newId("sys"), role: "system", content: "Voice recording is not available in this browser." }
      ]);
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunksRef.current = [];
    const recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) audioChunksRef.current.push(event.data);
    };
    recorder.onstop = () => {
      stream.getTracks().forEach((track) => track.stop());
      const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || "audio/webm" });
      const file = new File([blob], `voice-${new Date().toISOString().replace(/[:.]/g, "-")}.webm`, {
        type: blob.type || "audio/webm"
      });
      addFiles([file]);
    };
    mediaRecorderRef.current = recorder;
    recorder.start();
    setRecording(true);
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;
    setRecording(false);
  }

  async function submit() {
    if (!canSend || busy) return;
    const outgoingText = message.trim() || "Analyze the attached files.";
    const outgoingAttachments = attachments;
    setMessages((current) => [
      ...current,
      {
        id: newId("user"),
        role: "user",
        content: outgoingText,
        attachments: outgoingAttachments
      }
    ]);
    setMessage("");
    setAttachments([]);
    setBusy(true);
    try {
      let result: ChatResult;
      if (outgoingAttachments.length > 0) {
        const form = new FormData();
        form.append("message", outgoingText);
        form.append("priority", "5");
        form.append("wait", "true");
        outgoingAttachments.forEach((item) => form.append("files", item.file, item.name));
        const response = await fetch(apiUrl("/api/chat/upload"), {
          method: "POST",
          headers: apiAuthHeaders(),
          body: form,
          cache: "no-store"
        });
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}: ${await response.text()}`);
        result = await response.json();
      } else {
        result = await apiPost<ChatResult>("/api/chat/wait", { message: outgoingText, priority: 5 });
      }
      setMessages((current) => [
        ...current,
        {
          id: newId("assistant"),
          role: "assistant",
          content: result.response || "Completed without response.",
          status: result.status,
          taskId: result.task_id,
          attachments: (result.attachments || []).map((item) => ({
            id: item.id || newId("remote"),
            file: new File([], item.original_name, { type: item.content_type }),
            name: item.original_name,
            type: item.content_type,
            size: item.size,
            kind: item.kind
          }))
        }
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { id: newId("err"), role: "system", content: error instanceof Error ? error.message : "Chat request failed." }
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid h-[calc(100vh-5.5rem)] min-h-[720px] gap-4 xl:grid-cols-[1fr_320px]">
      <section className="soft-shadow flex min-h-0 flex-col rounded-[26px] border border-[#e4e9f0] bg-white">
        <div className="flex items-center justify-between border-b border-[#e4e9f0] p-5">
          <div>
            <h1 className="text-2xl font-black text-[#30343b]">Chat Console</h1>
            <div className="text-sm font-bold text-[#8c96a6]">Text, images, files, and voice notes</div>
          </div>
          <span className="rounded-full bg-[#e8f8f2] px-4 py-2 text-sm font-black text-[#23a978]">
            {busy ? "Running" : "Ready"}
          </span>
        </div>

        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto bg-[#f6f8fb] p-5">
          {messages.map((item) => (
            <div key={item.id} className={`flex ${item.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[78%] rounded-[24px] border p-4 ${
                  item.role === "user"
                    ? "border-[#2D8CFF] bg-[#2D8CFF] text-white shadow-[0_12px_24px_rgba(45,140,255,0.18)]"
                    : item.role === "assistant"
                      ? "border-[#e4e9f0] bg-white text-[#30343b]"
                      : "border-[#e4e9f0] bg-[#fff4d9] text-[#667085]"
                }`}
              >
                <div className="whitespace-pre-wrap text-sm font-bold leading-6">{item.content}</div>
                {item.taskId ? <div className="mt-3 text-xs font-black opacity-60">{item.taskId} · {item.status}</div> : null}
                {item.attachments?.length ? <AttachmentGrid items={item.attachments} compact={item.role === "user"} /> : null}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-[#e4e9f0] p-4">
          {attachments.length ? (
            <div className="mb-3 flex flex-wrap gap-2">
              {attachments.map((item) => (
                <button
                  key={item.id}
                  onClick={() => removeAttachment(item.id)}
                  className="inline-flex max-w-[240px] items-center gap-2 rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 py-2 text-xs font-black text-[#667085]"
                  title="Remove attachment"
                >
                  <AttachmentIcon kind={item.kind} />
                  <span className="truncate">{item.name}</span>
                  <X size={14} />
                </button>
              ))}
            </div>
          ) : null}
          <div className="grid gap-3 md:grid-cols-[auto_1fr_auto]">
            <div className="flex gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="grid h-12 w-12 place-items-center rounded-full bg-[#f6f8fb] text-[#2D8CFF] soft-shadow"
                title="Attach image or file"
              >
                <Paperclip size={18} />
              </button>
              <button
                onClick={recording ? stopRecording : startRecording}
                className={`grid h-12 w-12 place-items-center rounded-full soft-shadow ${recording ? "bg-[#fff0ea] text-[#ff5f3f]" : "bg-[#f6f8fb] text-[#2D8CFF]"}`}
                title={recording ? "Stop recording" : "Record voice"}
              >
                {recording ? <Square size={18} /> : <Mic size={18} />}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,audio/*,.pdf,.doc,.docx,.txt,.csv,.json,.zip"
                className="hidden"
                onChange={(event) => {
                  if (event.target.files) addFiles(event.target.files);
                  event.currentTarget.value = "";
                }}
              />
            </div>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submit();
                }
              }}
              placeholder="Type a message"
              className="min-h-12 resize-none rounded-[22px] border border-[#e4e9f0] bg-[#f6f8fb] px-4 py-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]"
            />
            <button
              onClick={submit}
              disabled={!canSend || busy}
              className="inline-flex h-12 items-center justify-center gap-2 rounded-full bg-[#2D8CFF] px-5 text-sm font-black text-white shadow-[0_12px_24px_rgba(45,140,255,0.22)] disabled:opacity-50"
            >
              <Send size={16} />
              Send
            </button>
          </div>
        </div>
      </section>

      <aside className="soft-shadow rounded-[26px] border border-[#e4e9f0] bg-white p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-black text-[#30343b]">Session</h2>
          <button
            onClick={() => {
              attachments.forEach((item) => item.url && URL.revokeObjectURL(item.url));
              setAttachments([]);
              setMessages([]);
            }}
            className="grid h-10 w-10 place-items-center rounded-full bg-[#f6f8fb] text-[#ff6b4a]"
            title="Clear chat"
          >
            <Trash2 size={16} />
          </button>
        </div>
        <div className="space-y-3">
          <InfoRow label="Messages" value={messages.length} />
          <InfoRow label="Pending files" value={attachments.length} />
          <InfoRow label="Max files" value="8" />
          <InfoRow label="Max size" value="25 MB" />
        </div>
        <div className="mt-5 rounded-[22px] bg-[#eaf4ff] p-4 text-sm font-bold leading-6 text-[#667085]">
          Voice notes are uploaded as audio attachments. Browser microphone permission is required for recording.
        </div>
      </aside>
    </div>
  );
}

function AttachmentIcon({ kind }: { kind: "image" | "voice" | "file" }) {
  if (kind === "image") return <FileImage size={16} />;
  if (kind === "voice") return <FileAudio size={16} />;
  return <FileText size={16} />;
}

function AttachmentGrid({ items, compact }: { items: AttachmentPreview[]; compact?: boolean }) {
  return (
    <div className="mt-3 grid gap-2">
      {items.map((item) => (
        <div key={item.id} className={`rounded-[18px] border p-3 ${compact ? "border-white/25 bg-white/10" : "border-[#e4e9f0] bg-[#f6f8fb]"}`}>
          {item.kind === "image" && item.url ? (
            <img src={item.url} alt={item.name} className="mb-2 max-h-56 w-full rounded-[14px] object-cover" />
          ) : null}
          {item.kind === "voice" && item.url ? <audio src={item.url} controls className="mb-2 w-full" /> : null}
          <div className="flex min-w-0 items-center gap-2 text-xs font-black">
            <AttachmentIcon kind={item.kind} />
            <span className="truncate">{item.name}</span>
            <span className="shrink-0 opacity-60">{formatBytes(item.size)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between rounded-[18px] bg-[#f6f8fb] px-4 py-3">
      <span className="text-sm font-bold text-[#8c96a6]">{label}</span>
      <span className="text-sm font-black text-[#30343b]">{value}</span>
    </div>
  );
}
