export type User = { id: number; email: string; full_name: string; account_type: string; is_active: boolean; is_platform_admin: boolean };
export type Organization = { id: number; name: string; slug: string; status: string };
export type Course = { id: number; title: string; slug: string; short_description: string | null; description: string | null; category_id: number | null; status: "draft" | "review" | "published" | "retired"; visibility: "public" | "private" | "organization"; level: string | null; estimated_hours: number | null; is_active: boolean; created_by_user_id: number };
export type CourseCategory = { id: number; name: string; slug: string; description: string | null };
export type CourseModule = { id: number; course_id: number; title: string; description: string | null; order_index: number };
export type Lesson = { id: number; module_id: number; title: string; slug: string; content_type: "text" | "video" | "document" | "quiz" | "lab_reference"; content: string | null; order_index: number; estimated_minutes: number | null; is_required: boolean };
